# Challenge 3: Generative AI for Data Analysis Support

## Challenge Description

This challenge focuses on creating an intelligent AI agent that empowers residents to conduct data analysis without requiring deep technical expertise. The agent acts as a bridge between residents' natural language questions about air quality and the underlying data analysis tools.

**The core idea**: Residents ask their questions naturally, the agent interprets the request, uses available data analysis tools to answer it, and provides results along with a complete audit trail showing which steps were taken.

## Problem Statement

Currently, data analysis is often a barrier for residents wanting to understand air quality in their area. They must either:
- Learn programming or statistical analysis
- Request analysis from experts (time-consuming and expensive)
- Use pre-built dashboards with limited flexibility

Your challenge is to develop an agent that:
1. Accepts natural language queries from residents (e.g., "Is the air quality better on weekends than weekdays?")
2. Interprets the question and determines what analysis is needed
3. Selects and executes appropriate data analysis tools
4. Combines results into a clear, understandable answer
5. Provides a complete audit trail of actions taken
6. Handles follow-up questions and refinements

## Approach

Build an AI agent using generative AI techniques:
- **Large Language Models (LLMs)**: GPT, Claude, or similar for understanding questions
- **Tool Integration**: Enable the agent to call data analysis functions
- **Chain-of-Thought Reasoning**: Decompose complex questions into analysis steps
- **Retrieval-Augmented Generation (RAG)**: Access relevant data and tool documentation
- **Structured Output**: Generate consistent, auditable results

## Required Data

1. **Sensor data**: Time-series air quality measurements from the Hollandse Luchten network
2. **Analysis capabilities inventory**: Comprehensive catalog of available data analysis functions, including:
   - Statistical functions (mean, median, standard deviation, trend analysis)
   - Time-series functions (seasonal decomposition, anomaly detection)
   - Geospatial functions (location-based filtering, geographic analysis)
   - Comparative analysis (before/after, day type comparison)
   - Visualization functions
3. **Code examples**: Sample implementations from the Samen Analyseren repository
4. **Tool specifications**: Detailed documentation of each available function (inputs, outputs, parameters)

## Key Questions to Address

1. **Question Understanding**: How accurately does the agent interpret resident questions?
2. **Tool Selection**: Can the agent correctly identify which analysis tools to use?
3. **Execution**: Does the agent properly combine multiple tools to answer complex questions?
4. **Result Communication**: Are answers clear and actionable for non-technical residents?
5. **Audit Trail**: Is the trail complete, understandable, and verifiable?
6. **Edge Cases**: How does the agent handle out-of-domain questions or ambiguous requests?
7. **Confidence**: Can the agent communicate uncertainty in its answers?

## Success Criteria

- Functional agent that understands natural language queries about air quality
- Ability to execute one or more data analysis tools in sequence
- Clear, resident-friendly results and explanations
- Complete audit trail showing all analysis steps
- Handles at least 5-10 common types of questions
- Graceful error handling for invalid or nonsensical queries

## Deliverables

1. **Agent Implementation**: Working code implementing the AI agent
2. **Tool Integration**: Complete integration with available data analysis functions
3. **Example Queries**: Demonstration of 5-10 representative questions and answers
4. **Audit Trail System**: Implementation showing how analysis steps are tracked and displayed
5. **User Interface**: Simple interface for residents to ask questions (CLI, web, or chat interface)
6. **Documentation**: 
   - User guide for asking questions
   - Developer guide for adding new tools
   - Technical architecture documentation
7. **Presentation**: 10-minute demonstration including live queries

## Resources

- Provided sensor data dump
- Comprehensive inventory of existing Samen Analyseren analysis functions and tools
- Python libraries: langchain, openai/anthropic APIs (or open-source LLMs)
- UI frameworks: streamlit (easy web interface) or Flask/FastAPI for custom interfaces
- Optional: Open-source LLMs (llama, mistral) if cloud APIs not preferred

## Sample Question Types

To help guide development, consider supporting these question categories:

1. **Temporal Comparison**: "How does January compare to December for air quality?"
2. **Location Analysis**: "Which sensor has the worst air quality in our neighborhood?"
3. **Trend Analysis**: "Is air quality improving or getting worse this year?"
4. **Anomaly Detection**: "Were there any unusual air quality events last month?"
5. **Comparative Analysis**: "Is air quality better on weekends vs. weekdays?"
6. **Source Investigation**: "Which direction does the pollution come from when it's bad?"
7. **Statistical Summaries**: "What's the average air quality in our area?"
8. **Alerts/Thresholds**: "When did air quality exceed safe levels?"
9. **Forecasting Support**: "Based on current trends, how will next week's air quality look?"
10. **User Education**: "What factors influence air quality measurements?"

## Tips

- Start with a small set of well-defined questions and gradually expand
- Use concrete example analyses from Samen Analyseren as templates
- Test with actual residents to understand how they naturally phrase questions
- Build a fallback system for questions you can't handle ("I don't know how to answer that")
- Consider context from previous questions (conversational memory)
- Prioritize clarity and correctness over trying to answer everything
- Make the audit trail visually appealing and easy to understand
- Start with simple tools before adding complex analysis chains
- Use prompt engineering to guide the agent's reasoning
- Consider using few-shot learning with examples to improve performance

---

[Back to main README](../README.md)
