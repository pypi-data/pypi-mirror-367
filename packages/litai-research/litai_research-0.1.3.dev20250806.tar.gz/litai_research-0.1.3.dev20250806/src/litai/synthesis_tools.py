"""Atomic tools for conversational paper synthesis."""

import asyncio
import json
from dataclasses import dataclass
from litai.database import Database
from litai.llm import LLMClient
from litai.models import Paper
from litai.extraction import PaperExtractor, KeyPoint
from litai.utils.logger import get_logger
from rich.live import Live
from rich.text import Text

logger = get_logger(__name__)

# OpenAI-style tool definitions for the LLM
SYNTHESIS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": "Search for papers in the collection and automatically select them for synthesis. The found papers will be added to your current session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query or topic (e.g., 'attention mechanisms', 'deep learning')"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags to filter by"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of papers to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "select_papers",
            "description": "Manually select specific papers by their IDs (use this only if you need to modify the selection after searching). Can set, add to, or remove from current selection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of paper IDs to select"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["set", "add", "remove"],
                        "description": "How to modify the selection: 'set' replaces, 'add' appends, 'remove' deletes",
                        "default": "set"
                    }
                },
                "required": ["paper_ids"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_selected_papers",
            "description": "Show currently selected papers in the synthesis session",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_context",
            "description": "Extract context from selected papers at specified depth level for synthesis",
            "parameters": {
                "type": "object",
                "properties": {
                    "depth": {
                        "type": "string",
                        "enum": ["abstracts", "key_points", "notes", "sections", "full_text"],
                        "description": "Level of detail to extract: abstracts (quick), key_points (medium), notes (user notes), sections (specific), full_text (complete)"
                    },
                    "sections": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific section names if depth='sections' (e.g., ['Introduction', 'Methods'])"
                    }
                },
                "required": ["depth"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "synthesize",
            "description": "Generate a synthesis from the current context to answer a research question",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Research question to answer using the selected papers"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["quick", "thorough", "comparative"],
                        "description": "Synthesis mode: quick (main points), thorough (detailed), comparative (compare/contrast)",
                        "default": "quick"
                    }
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "refine_synthesis",
            "description": "Refine or go deeper on the previous synthesis with additional focus",
            "parameters": {
                "type": "object",
                "properties": {
                    "refinement": {
                        "type": "string",
                        "description": "How to refine the synthesis (e.g., 'go deeper on methods', 'focus on results', 'compare approaches')"
                    }
                },
                "required": ["refinement"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_session_state",
            "description": "Get current session state including selected papers, context depth, and synthesis history",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


@dataclass
class ExtractedContext:
    """Context extracted from a paper."""
    paper_id: str
    context_type: str
    content: str
    metadata: dict[str, str] | None = None


class PaperSelector:
    """Tool for selecting papers based on flexible criteria."""
    
    def __init__(self, db: Database, llm: LLMClient):
        self.db = db
        self.llm = llm
        
    async def select_papers(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
        paper_ids: list[str] | None = None,
        limit: int | None = None
    ) -> list[Paper]:
        """Select papers based on flexible criteria.
        
        Args:
            query: Natural language query for semantic selection
            tags: Filter by tags
            paper_ids: Specific paper IDs to select
            limit: Maximum number of papers to return
            
        Returns:
            List of selected papers
        """
        # Start with all papers
        papers = self.db.list_papers(limit=100)
        logger.info(f"Starting with {len(papers)} total papers in collection")
        
        # Filter by specific IDs if provided
        if paper_ids:
            papers = [p for p in papers if p.paper_id in paper_ids]
            logger.info(f"After filtering by paper_ids: {len(papers)} papers")
            
        # Filter by tags if provided
        if tags:
            initial_count = len(papers)
            papers = [p for p in papers if any(tag in p.tags for tag in tags)]
            logger.info(f"After filtering by tags {tags}: {initial_count} -> {len(papers)} papers")
            
        # Semantic selection based on query
        # Skip semantic selection if query is just asking for papers by tag
        if query:
            # Check if query is essentially just requesting papers with the specified tags
            query_lower = query.lower().strip()
            is_tag_only_query = tags and any(
                tag in query_lower and ('tag' in query_lower or 'pull' in query_lower or 'get' in query_lower)
                for tag in tags
            )
            
            if not is_tag_only_query:
                initial_count = len(papers)
                papers = await self._semantic_select(query, papers)
                logger.info(f"After semantic selection for '{query}': {initial_count} -> {len(papers)} papers")
            else:
                logger.info(f"Skipping semantic selection for tag-only query: '{query}'")
            
        # Apply limit
        if limit:
            initial_count = len(papers)
            papers = papers[:limit]
            if initial_count > limit:
                logger.info(f"Applied limit of {limit}: {initial_count} -> {len(papers)} papers")
            
        logger.info(f"Final selection: {len(papers)} papers")
        return papers
        
    async def _semantic_select(self, query: str, papers: list[Paper]) -> list[Paper]:
        """Use LLM to select papers semantically relevant to query."""
        if not papers:
            return []
            
        logger.info(f"Running semantic selection on {len(papers)} papers for query: '{query}'")
        
        # Format papers for LLM
        paper_list = "\n".join([
            f'{i + 1}. "{paper.title}" ({paper.year})\n'
            f"   Abstract: {paper.abstract[:150]}..."
            for i, paper in enumerate(papers)
        ])
        
        prompt = f"""Given this query: "{query}"

Select papers relevant to this query from:
{paper_list}

Return a JSON list of paper numbers (1-indexed) that are relevant.
Example: [1, 3, 5]"""
        
        response = await self.llm.complete(prompt, max_tokens=200)
        
        try:
            # Extract JSON from response
            content = response["content"].strip()
            logger.info(f"LLM response for semantic selection: {content}")
            
            # Find JSON array in the response
            import re
            json_match = re.search(r'\[[\d,\s]+\]', content)
            if json_match:
                selected_indices = json.loads(json_match.group())
                logger.info(f"LLM selected paper indices: {selected_indices}")
                
                selected_papers = [
                    papers[i - 1] 
                    for i in selected_indices 
                    if 1 <= i <= len(papers)
                ]
                logger.info(f"Semantic selection returned {len(selected_papers)} papers")
                return selected_papers
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Failed to parse LLM selection: {e}")
            
        logger.warning("Semantic selection fallback - returning first 10 papers")
        return papers[:10]  # Fallback to first 10


class ContextExtractor:
    """Tool for extracting different types of context from papers."""
    
    def __init__(self, db: Database, extractor: PaperExtractor):
        self.db = db
        self.extractor = extractor
        # Access pdf_processor through extractor
        self.pdf_processor = extractor.pdf_processor
        
    async def extract_context(
        self,
        papers: list[Paper],
        context_type: str = "abstracts",
        sections: list[str] | None = None
    ) -> dict[str, ExtractedContext]:
        """Extract specified context from papers.
        
        Args:
            papers: Papers to extract from
            context_type: Type of context to extract
                - "abstracts": Just the abstracts
                - "notes": User's notes on papers
                - "key_points": Extracted claims/evidence
                - "full_text": Complete paper text
                - "sections": Specific sections
            sections: For context_type="sections", which sections to extract
            
        Returns:
            Dictionary mapping paper_id to extracted context
        """
        contexts = {}
        
        for paper in papers:
            logger.info(f"Extracting {context_type} from {paper.title}")
            
            if context_type == "abstracts":
                content = paper.abstract
                
            elif context_type == "notes":
                # Get user notes from database
                notes = self.db.get_note(paper.paper_id)
                content = notes if notes else "No notes available"
                
            elif context_type == "key_points":
                # Extract key points
                try:
                    key_points = await self.extractor.extract_key_points(paper.paper_id)
                    content = self._format_key_points(key_points)
                except Exception as e:
                    logger.warning(f"Failed to extract key points: {e}")
                    content = "Key point extraction failed"
                    
            elif context_type == "full_text":
                # Get full text from storage (download if needed)
                try:
                    full_text = await self.pdf_processor.process_paper(paper.paper_id)
                    content = full_text if full_text else paper.abstract
                except Exception as e:
                    logger.warning(f"Failed to read full text: {e}")
                    content = paper.abstract  # Fallback to abstract
                    
            elif context_type == "sections" and sections:
                # Extract specific sections
                try:
                    full_text = await self.pdf_processor.process_paper(paper.paper_id)
                    if full_text:
                        content = self._extract_sections(full_text, sections)
                    else:
                        content = paper.abstract
                except Exception as e:
                    logger.warning(f"Failed to extract sections: {e}")
                    content = paper.abstract
                    
            else:
                content = paper.abstract  # Default fallback
                
            contexts[paper.paper_id] = ExtractedContext(
                paper_id=paper.paper_id,
                context_type=context_type,
                content=content,
                metadata={"title": paper.title, "year": str(paper.year)}
            )
            
        return contexts
        
    def _format_key_points(self, key_points: list[KeyPoint]) -> str:
        """Format key points as readable text."""
        if not key_points:
            return "No key points extracted"
            
        lines = []
        for point in key_points:
            lines.append(f"• {point.claim}")
            lines.append(f"  Evidence: {point.evidence}")
            lines.append(f"  Section: {point.section}")
            lines.append("")
        return "\n".join(lines)
        
    def _extract_sections(self, full_text: str, sections: list[str]) -> str:
        """Extract specific sections from full text."""
        extracted = []
        text_lower = full_text.lower()
        
        for section in sections:
            # Try to find section headers
            patterns = [
                f"\n{section.lower()}\n",
                f"\n{section.lower()}:",
                f"\n## {section.lower()}",
                f"\n### {section.lower()}",
            ]
            
            for pattern in patterns:
                if pattern in text_lower:
                    # Find the section and extract until next major section
                    start = text_lower.index(pattern)
                    # Find next section or end
                    next_section = len(full_text)
                    for next_pattern in ["\n## ", "\n### ", "\nreferences", "\nappendix"]:
                        idx = text_lower.find(next_pattern, start + len(pattern))
                        if idx != -1 and idx < next_section:
                            next_section = idx
                    
                    section_text = full_text[start:next_section].strip()
                    extracted.append(f"=== {section.upper()} ===\n{section_text}")
                    break
                    
        return "\n\n".join(extracted) if extracted else "Sections not found"


class QuestionAnswerer:
    """Tool for generating answers from context."""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
        
    async def answer(
        self,
        question: str,
        context: dict[str, ExtractedContext],
        papers: list[Paper],
        depth: str = "quick"
    ) -> str:
        """Generate answer from context.
        
        Args:
            question: Question to answer
            context: Extracted context from papers
            papers: Original paper objects for metadata
            depth: Answer depth
                - "quick": Brief answer with key points
                - "thorough": Detailed analysis
                - "comparative": Focus on comparing papers
                
        Returns:
            Generated answer text
        """
        # Build context string
        context_parts = []
        paper_map = {p.paper_id: p for p in papers}
        
        for i, (paper_id, ctx) in enumerate(context.items(), 1):
            paper = paper_map.get(paper_id)
            if paper:
                context_parts.append(f"[{i}] {paper.title} ({paper.year})")
                context_parts.append(f"Context type: {ctx.context_type}")
                context_parts.append(ctx.content[:1500])  # Limit context length
                context_parts.append("")
                
        context_str = "\n".join(context_parts)
        
        # Build appropriate prompt based on depth
        if depth == "quick":
            prompt = f"""Question: {question}

Context from papers:
{context_str}

Provide a brief, direct answer using the context. Use citations [1], [2], etc."""
            
        elif depth == "thorough":
            prompt = f"""Question: {question}

Context from papers:
{context_str}

Provide a comprehensive analysis that:
1. Directly answers the question
2. Synthesizes findings from all relevant papers
3. Uses citations [1], [2], etc.
4. Identifies key themes and patterns
5. Notes any limitations or gaps"""
            
        elif depth == "comparative":
            prompt = f"""Question: {question}

Context from papers:
{context_str}

Compare and contrast the papers:
1. How do they approach this question differently?
2. What do they agree on?
3. Where do they disagree?
4. What unique contributions does each make?
Use citations [1], [2], etc."""
            
        else:
            prompt = f"""Question: {question}

Context: {context_str}

Answer the question based on the context. Use citations."""
            
        response = await self.llm.complete(
            prompt, 
            max_tokens=1500 if depth == "thorough" else 800
        )
        
        return response["content"].strip()


class SynthesisOrchestrator:
    """Orchestrates the atomic tools for conversational synthesis."""
    
    def __init__(
        self,
        db: Database,
        llm: LLMClient,
        extractor: PaperExtractor
    ):
        self.selector = PaperSelector(db, llm)
        self.context_extractor = ContextExtractor(db, extractor)
        self.answerer = QuestionAnswerer(llm)
        
        # State for conversational flow
        self.current_papers: list[Paper] = []
        self.current_context: dict[str, ExtractedContext] = {}
        self.current_question: str = ""
        
    async def synthesize(
        self,
        question: str,
        tags: list[str] | None = None,
        paper_ids: list[str] | None = None,
        context_type: str = "abstracts",
        depth: str = "quick"
    ) -> dict[str, str | list[Paper]]:
        """Main synthesis entry point.
        
        Returns:
            Dictionary with 'answer', 'papers', and 'context_type'
        """
        # Select papers
        self.current_papers = await self.selector.select_papers(
            query=question,
            tags=tags,
            paper_ids=paper_ids
        )
        
        if not self.current_papers:
            return {
                "answer": "No relevant papers found in your library.",
                "papers": [],
                "context_type": context_type
            }
        
        # Extract context
        self.current_context = await self.context_extractor.extract_context(
            self.current_papers,
            context_type=context_type
        )
        
        # Generate answer
        self.current_question = question
        answer = await self.answerer.answer(
            question,
            self.current_context,
            self.current_papers,
            depth=depth
        )
        
        return {
            "answer": answer,
            "papers": self.current_papers,
            "context_type": context_type
        }
        
    async def refine(
        self,
        refinement: str,
        context_type: str | None = None,
        depth: str | None = None
    ) -> dict[str, str | list[Paper]]:
        """Refine the current synthesis based on user feedback.
        
        Args:
            refinement: User's refinement request
            context_type: Optional new context type
            depth: Optional new depth level
            
        Returns:
            Updated synthesis result
        """
        # Update context if requested
        if context_type and context_type != self.current_context.get("type"):
            self.current_context = await self.context_extractor.extract_context(
                self.current_papers,
                context_type=context_type
            )
            
        # Generate refined answer
        combined_question = f"{self.current_question}\n\nRefinement: {refinement}"
        answer = await self.answerer.answer(
            combined_question,
            self.current_context,
            self.current_papers,
            depth=depth or "quick"
        )
        
        return {
            "answer": answer,
            "papers": self.current_papers,
            "context_type": context_type or "current"
        }
        
    async def add_papers(self, paper_ids: list[str]) -> None:
        """Add more papers to current synthesis session."""
        new_papers = await self.selector.select_papers(paper_ids=paper_ids)
        
        # Add to current papers (avoid duplicates)
        current_ids = {p.paper_id for p in self.current_papers}
        for paper in new_papers:
            if paper.paper_id not in current_ids:
                self.current_papers.append(paper)
                
        # Extract context for new papers
        new_context = await self.context_extractor.extract_context(
            new_papers,
            context_type=list(self.current_context.values())[0].context_type
            if self.current_context else "abstracts"
        )
        self.current_context.update(new_context)
        
    async def change_context_depth(self, context_type: str) -> None:
        """Change the context extraction depth for current papers."""
        self.current_context = await self.context_extractor.extract_context(
            self.current_papers,
            context_type=context_type
        )


class SynthesisConversation:
    """Manages LLM-driven conversations with tool use for synthesis."""
    
    def __init__(self, db: Database, llm: LLMClient, orchestrator: SynthesisOrchestrator):
        self.db = db
        self.llm = llm
        self.orchestrator = orchestrator
        from litai.synthesis_session import SynthesisSession
        self.session = SynthesisSession()
        self.tools = self._create_tool_handlers()
        self.message_history = []
        self.live = None  # Rich Live display for tool calls
        
    def _create_tool_handlers(self):
        """Map tool names to actual implementation functions."""
        return {
            "search_papers": self._search_papers,
            "select_papers": self._select_papers,
            "list_selected_papers": self._list_selected_papers,
            "extract_context": self._extract_context,
            "synthesize": self._synthesize,
            "refine_synthesis": self._refine_synthesis,
            "get_session_state": self._get_session_state
        }
    
    async def handle_message(self, user_message: str) -> str:
        """Main conversation loop handler."""
        # Build system prompt with current state
        system_prompt = self._build_system_prompt()
        
        # Add user message to history
        self.message_history.append({"role": "user", "content": user_message})
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": system_prompt},
            *self.message_history[-10:]  # Keep last 10 messages for context
        ]
        
        # Get LLM response with tool access
        response = await self.llm.complete(
            messages,
            tools=SYNTHESIS_TOOLS
        )
        
        # Handle tool calls if any
        if "tool_calls" in response and response["tool_calls"]:
            tool_results = []
            
            # Create Live display for showing tool progress
            with Live(refresh_per_second=10) as live:
                for i, tool_call in enumerate(response["tool_calls"]):
                    # Create flashing animation for current tool
                    for flash_cycle in range(3):  # Flash 3 times
                        # Flash on (bright)
                        tool_display = Text()
                        tool_display.append("⚡ ", style="bold yellow blink")
                        tool_display.append(f"{tool_call.name}", style="bold yellow")
                        if hasattr(tool_call, 'arguments') and tool_call.arguments:
                            # Show brief argument summary
                            args_str = str(tool_call.arguments)
                            if len(args_str) > 50:
                                args_str = args_str[:47] + "..."
                            tool_display.append(f" ({args_str})", style="dim")
                        
                        live.update(tool_display)
                        await asyncio.sleep(0.15)
                        
                        # Flash off (dimmer)
                        tool_display = Text()
                        tool_display.append("◯ ", style="dim")
                        tool_display.append(f"{tool_call.name}", style="dim")
                        if hasattr(tool_call, 'arguments') and tool_call.arguments:
                            args_str = str(tool_call.arguments)
                            if len(args_str) > 50:
                                args_str = args_str[:47] + "..."
                            tool_display.append(f" ({args_str})", style="dim")
                        
                        live.update(tool_display)
                        await asyncio.sleep(0.15)
                    
                    logger.info(f"Executing tool: {tool_call.name}")
                    result = await self._execute_tool(
                        tool_call.name,
                        tool_call.arguments
                    )
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result) if not isinstance(result, str) else result
                    })
                    
                    # Show green checkmark when complete
                    tool_display = Text()
                    tool_display.append("✓ ", style="bold green")
                    tool_display.append(f"{tool_call.name}", style="green")
                    tool_display.append(" complete", style="dim green")
                    
                    live.update(tool_display)
                    await asyncio.sleep(0.5)
            
            # Add assistant response with tool calls to history
            self.message_history.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else tc.arguments
                        }
                    } for tc in response["tool_calls"]
                ]
            })
            
            # Add tool results to history
            for result in tool_results:
                self.message_history.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": result["content"]
                })
            
            # Get final response with tool results
            messages = [
                {"role": "system", "content": system_prompt},
                *self.message_history[-15:]  # Include tool results
            ]
            
            response = await self.llm.complete(
                messages,
                tools=SYNTHESIS_TOOLS
            )
        
        # Add final response to history
        final_content = response.get("content", "")
        self.message_history.append({"role": "assistant", "content": final_content})
        
        return final_content
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with current session state."""
        paper_count = len(self.session.selected_papers)
        paper_list = ""
        if paper_count > 0:
            paper_list = "\n".join([
                f"- {p.title} ({p.year})"
                for p in self.session.selected_papers[:5]
            ])
            if paper_count > 5:
                paper_list += f"\n... and {paper_count - 5} more"
                
        return f"""You are a research synthesis assistant helping analyze academic papers.

Current session state:
- Papers selected: {paper_count}
- Context depth: {self.session.context_type}
- Previous syntheses: {len(self.session.synthesis_history)}

{"Selected papers:" if paper_count > 0 else "No papers selected yet."}
{paper_list}

You have access to tools for searching, selecting, and synthesizing papers.
Use them naturally based on the conversation. When greeting, just respond 
conversationally without using tools. Be concise and helpful."""
    
    async def _execute_tool(self, tool_name: str, arguments: dict) -> dict | str:
        """Execute a tool and return its result."""
        handler = self.tools.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            result = await handler(**arguments)
            return result
        except Exception as e:
            logger.exception(f"Tool execution failed: {tool_name}")
            return {"error": str(e)}
    
    async def _search_papers(self, query: str, tags: list[str] | None = None, limit: int = 10) -> dict:
        """Search for papers using the selector."""
        logger.info(f"Searching papers with query='{query}', tags={tags}, limit={limit}")
        
        papers = await self.orchestrator.selector.select_papers(
            query=query,
            tags=tags,
            limit=limit
        )
        
        # Always auto-select found papers since this tool now searches AND selects
        # ADD them to existing selection instead of replacing
        if papers:
            logger.info(f"Auto-selecting {len(papers)} papers for query='{query}'")
            await self.session.update_papers(add_papers=papers)
        
        return {
            "found": len(papers),
            "papers": [
                {
                    "id": p.paper_id,
                    "title": p.title,
                    "year": p.year,
                    "tags": p.tags,
                    "abstract_preview": p.abstract[:200] + "..." if len(p.abstract) > 200 else p.abstract
                }
                for p in papers
            ],
            "auto_selected": bool(papers)  # Always true if papers found
        }
    
    async def _select_papers(self, paper_ids: list[str], operation: str = "set") -> dict:
        """Select papers for synthesis."""
        logger.info(f"Selecting papers: operation={operation}, paper_ids={paper_ids}")
        
        if operation == "set":
            # Get papers by IDs
            papers = [self.db.get_paper(pid) for pid in paper_ids]
            papers = [p for p in papers if p]  # Filter out None
            await self.session.update_papers(papers=papers)
        elif operation == "add":
            papers = [self.db.get_paper(pid) for pid in paper_ids]
            papers = [p for p in papers if p]
            await self.session.update_papers(add_papers=papers)
        elif operation == "remove":
            await self.session.update_papers(remove_paper_ids=paper_ids)
        
        logger.info(f"Papers selected: {len(self.session.selected_papers)} total")
        return {
            "operation": operation,
            "selected_count": len(self.session.selected_papers),
            "papers": [p.title for p in self.session.selected_papers]
        }
    
    async def _list_selected_papers(self) -> dict:
        """List currently selected papers."""
        logger.info(f"Listing selected papers: {len(self.session.selected_papers)} papers")
        return {
            "count": len(self.session.selected_papers),
            "papers": [
                {
                    "id": p.paper_id,
                    "title": p.title,
                    "year": p.year,
                    "tags": p.tags
                }
                for p in self.session.selected_papers
            ]
        }
    
    async def _extract_context(self, depth: str, sections: list[str] | None = None) -> dict:
        """Extract context from selected papers."""
        if not self.session.selected_papers:
            return {"error": "No papers selected. Use search_papers and select_papers first."}
        
        # Update context depth in session
        await self.session.change_context_depth(depth, sections)
        
        # Extract context
        self.orchestrator.current_context = await self.orchestrator.context_extractor.extract_context(
            self.session.selected_papers,
            context_type=depth,
            sections=sections
        )
        
        return {
            "depth": depth,
            "papers_processed": len(self.orchestrator.current_context),
            "context_preview": "Context extracted successfully"
        }
    
    async def _synthesize(self, question: str, mode: str = "quick") -> dict:
        """Generate synthesis from current context."""
        if not self.session.selected_papers:
            return {"error": "No papers selected. Use search_papers and select_papers first."}
        
        # Ensure we have context
        if not self.orchestrator.current_context:
            # Extract default context
            self.orchestrator.current_context = await self.orchestrator.context_extractor.extract_context(
                self.session.selected_papers,
                context_type=self.session.context_type
            )
        
        # Generate synthesis
        self.session.current_question = question
        answer = await self.orchestrator.answerer.answer(
            question,
            self.orchestrator.current_context,
            self.session.selected_papers,
            depth=mode
        )
        
        # Store in history
        from litai.synthesis import SynthesisResult
        result = SynthesisResult(
            question=question,
            synthesis=answer,
            papers_used=[p.paper_id for p in self.session.selected_papers],
            context_type=self.session.context_type
        )
        self.session.add_synthesis_result(result)
        
        return {
            "question": question,
            "mode": mode,
            "synthesis": answer
        }
    
    async def _refine_synthesis(self, refinement: str) -> dict:
        """Refine the previous synthesis."""
        if not self.session.synthesis_history:
            return {"error": "No previous synthesis to refine. Use synthesize first."}
        
        # Build refined question
        combined_question = f"{self.session.current_question}\n\nRefinement: {refinement}"
        
        # Generate refined answer
        answer = await self.orchestrator.answerer.answer(
            combined_question,
            self.orchestrator.current_context,
            self.session.selected_papers,
            depth="thorough"
        )
        
        # Store refined result
        from litai.synthesis import SynthesisResult
        result = SynthesisResult(
            question=combined_question,
            synthesis=answer,
            papers_used=[p.paper_id for p in self.session.selected_papers],
            context_type=self.session.context_type
        )
        self.session.add_synthesis_result(result)
        
        return {
            "refinement": refinement,
            "synthesis": answer
        }
    
    async def _get_session_state(self) -> dict:
        """Get current session state."""
        summary = self.session.get_summary()
        return {
            "papers_selected": summary["papers_count"],
            "paper_titles": summary["paper_titles"],
            "context_type": summary["context_type"],
            "current_question": summary["current_question"],
            "synthesis_count": summary["synthesis_count"],
            "session_duration_minutes": summary["session_duration_minutes"]
        }
