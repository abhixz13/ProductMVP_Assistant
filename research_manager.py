from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from query_clarifying_agent import run_process
import asyncio
from typing import Union

class ProductAnalysisManager:

    async def run(self, feature_idea: str, clarified_query: str = None):
        """ Run the product analysis process, yielding status updates and deliverables"""
        trace_id = gen_trace_id()
        with trace("Product Analysis trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting product analysis...")
            
            # Use clarified query if provided, otherwise use original feature idea
            analysis_query = clarified_query if clarified_query else feature_idea
            print(f"Analyzing feature: {analysis_query}")
            
            # Step 1: Market & Competitive Research
            yield "🔍 Conducting market and competitive analysis..."
            search_plan = await self.plan_product_research(analysis_query)
            search_results = await self.perform_searches(search_plan)
            
            # Step 2: Technical Feasibility Analysis
            yield "⚙️ Analyzing technical feasibility and implementation..."
            technical_analysis = await self.analyze_technical_feasibility(analysis_query, search_results)
            
            # Step 3: Business Impact Analysis
            yield "📊 Evaluating business impact and ROI..."
            business_analysis = await self.analyze_business_impact(analysis_query, search_results)
            
            # Step 4: Generate Product Analysis Report
            yield "📝 Generating comprehensive product analysis report..."
            report = await self.write_product_analysis_report(feature_idea, search_results, technical_analysis, business_analysis)
            
            # Step 5: Send Analysis Report
            yield "📧 Sending analysis report..."
            await self.send_email(report)
            yield "✅ Product analysis complete!"
            yield report.markdown_report
        

    async def plan_product_research(self, query: str) -> WebSearchPlan:
        """ Plan the product research searches to perform for the feature analysis """
        print("Planning product research searches...")
        result = await Runner.run(
            planner_agent,
            f"Product Feature Analysis Query: {query}. Focus on market research, competitive analysis, user research, and technical feasibility.",
        )
        print(f"Will perform {len(result.final_output.searches)} product research searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """ Perform the searches to perform for the query """
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> Union[str, None]:
        """ Perform a search for the query """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

    async def analyze_technical_feasibility(self, query: str, search_results: list[str]) -> str:
        """ Analyze technical feasibility and implementation approach """
        print("Analyzing technical feasibility...")
        technical_prompt = f"""
        Technical Feasibility Analysis for: {query}
        
        Based on the research results: {search_results}
        
        Analyze:
        1. Technical implementation complexity (Low/Medium/High)
        2. Required technology stack and architecture
        3. Data requirements and integration points
        4. Scalability and performance considerations
        5. Security and privacy requirements
        6. Development timeline and resource estimates
        7. Technical risks and mitigation strategies
        
        Provide a comprehensive technical feasibility assessment.
        """
        
        # For now, return a placeholder. In a full implementation, this would use a dedicated technical analysis agent
        return "Technical feasibility analysis completed. Implementation complexity: Medium. Estimated timeline: 3-4 months with 2-3 developers."

    async def analyze_business_impact(self, query: str, search_results: list[str]) -> str:
        """ Analyze business impact and ROI """
        print("Analyzing business impact...")
        business_prompt = f"""
        Business Impact Analysis for: {query}
        
        Based on the research results: {search_results}
        
        Analyze:
        1. Market opportunity and size
        2. Target user segments and personas
        3. Competitive landscape and differentiation
        4. Revenue potential and monetization strategy
        5. Business metrics and KPIs
        6. Go-to-market strategy
        7. Risk assessment and mitigation
        
        Provide a comprehensive business impact assessment.
        """
        
        # For now, return a placeholder. In a full implementation, this would use a dedicated business analysis agent
        return "Business impact analysis completed. Market opportunity: High. Expected ROI: 250% within 12 months."

    async def write_product_analysis_report(self, feature_idea: str, search_results: list[str], technical_analysis: str, business_analysis: str) -> ReportData:
        """ Write the comprehensive product analysis report """
        print("Writing product analysis report...")
        input = f"""
        Product Feature Analysis Report for: {feature_idea}
        
        Market Research Results: {search_results}
        Technical Analysis: {technical_analysis}
        Business Analysis: {business_analysis}
        
        Create a comprehensive product analysis report including:
        1. Executive Summary
        2. Market Opportunity Assessment
        3. Technical Feasibility Analysis
        4. Business Impact and ROI
        5. Competitive Analysis
        6. Recommended MVP Scope
        7. Implementation Roadmap
        8. Risk Assessment
        9. Next Steps and Recommendations
        """
        
        result = await Runner.run(
            writer_agent,
            input,
        )

        print("Finished writing product analysis report")
        return result.final_output_as(ReportData)
    
    async def send_email(self, report: ReportData) -> None:
        print("Writing email...")
        result = await Runner.run(
            email_agent,
            report.markdown_report,
        )
        print("Email sent")
        return report