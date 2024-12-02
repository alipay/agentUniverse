# Domain Component Principles
agentUniverse includes several domain components, which combine to form the fundamental components of the multi-agent framework, including:
* Agent
* LLM
* Tool
* Knowledge
* Memory
* Planner

All domain components in agentUniverse follow a unified design philosophy, exhibiting the following characteristics:

* Development is configuration-oriented, enhancing the efficiency of component creation and reuse.
* Possess independent managers, providing a unified and isolated mechanism for component registration and management.
* Standard domain definitions support the injection of all similar type components in the industry.
* Components are customizable, opening up capabilities for all domain components to be tailored.

This chapter will specifically introduce the design principles of each domain component and how to use them. Please read the sub-documents within this chapter.