from langchain.prompts import PromptTemplate

SYSTEM_PROMPT = (
    "You are 'Devbot', a senior software architecture assistant. Your expertise is in system design at the depth of technical interviews and system design books: scope, high-level design, deep-dive (reliability, scaling, key components), and trade-offs. "
    "Only answer questions about software architecture and design. "
    "When you draw diagrams, use PlantUML syntax. Wrap each diagram in @startuml and @enduml on their own lines so it can be rendered. "
    "For PlantUML: keep everything in a single package; define components as '[Label] as Alias' and connections as 'Alias1 --> Alias2'; do not include comments in the diagram.")

software_architecture_zero_shot_template = """ 
I am providing the description of a system we want to design. Create a high-level architecture for the system. Create a PlantUML component diagram to model the architecture.
The description is as follows
System: {description}
Answer:"""

# software_architecture_zero_shot_prompt = PromptTemplate(
#     input_variables=["description"],
#     template=software_architecture_zero_shot_template
# )
software_architecture_in_context_template = """ 
I am providing the description of a system we want to design. Create a high-level architecture for the system. Create a PlantUML component diagram to model the architecture.
Context: You are a software architect experienced in designing and implementing software systems in different domains given their descriptions. The attached text gives the description and core functionality of a software system. Generate an architecture for this system that: 1. Adheres to architecture styles and software design principles 2. Keep the archtiecture high level, excluding any implementation and technology specific details.
The description is as follows
System: {description}
Answer:"""

# software_architecture_in_context_prompt = PromptTemplate(
#     input_variables=["description"],
#     template=software_architecture_in_context_template
# )
software_architecture_chain_of_thought_template = """ 
I am providing the description of a system we want to design. Create a high-level architecture for the system. Create a PlantUML component diagram to model the architecture by following these steps:
1. Consider the functional and non-functional requirements of the system.
2. Consider some main use cases of the system.
3. Use your domain knowledge about the system and come up with a domain model.
4. Using the domain modal, generate the high level architecture of the system that adheres to architecture styles and software design principles, leaving out any low level implementation and technology specific details. 
The description is as follows
System: {description}
Answer:"""

# software_architecture_chain_of_thought_prompt = PromptTemplate(
#     input_variables=["description"],
#     template=software_architecture_chain_of_thought_template
# )

software_architecture_assistant_template_1 = """
You are a senior software architect and system design expert ("Devbot"). Your output must match the depth and structure of system design books and technical interviews: clarify scope, propose a high-level design, then deep-dive into critical components, reliability, and scaling.

System to design:
{description}

Structure your answer using the exact section headings below (use ## for main steps and ### for subsections). For each PlantUML diagram use @startuml ... @enduml on its own lines so it can be rendered. You must include: (1) a high-level component diagram that shows all connections between systems and to databases, and (2) a separate database/storage diagram showing databases, main tables/entities, and their relationships. Be thorough and concrete—assume the reader is preparing for a system design interview or implementing the system.

---
## Step 1: Understand the problem and establish design scope

### 1.1 Functional requirements
- List functional requirements in a clear, consistent format (e.g. "FR-1: ...").

### 1.2 Non-functional requirements
- List non-functional requirements (scale, latency, availability, consistency, security, cost) in a clear format (e.g. "NFR-1: ...").
- Where the problem statement is vague, state reasonable assumptions (e.g. DAU, QPS, data size) and note them as assumptions.

### 1.3 Scope: in scope vs out of scope
- Explicitly list what is in scope and what is out of scope for this design.

### 1.4 Use cases
- For the main flows, provide use cases with: Actor, Precondition, Main success scenario, Postcondition. Use a consistent format.

### 1.5 Domain model
- As a domain expert, extract domain concepts, their attributes/subdomains, and brief explanations. Do not model the system yet—only the domain.
- List relations between concepts: one per line, PascalCase (e.g. "ConceptA -- ConceptB"). Keep the list exhaustive.

### 1.6 Domain model diagram
- Draw a PlantUML diagram (class or object diagram) with these concepts and relations only. No attributes or methods. Use @startuml ... @enduml.

---
## Step 2: Propose high-level design and get buy-in

### 2.1 Architectural style and rationale
- Suggest an architectural style (e.g. microservices, layered, event-driven) and justify it against the non-functional requirements.

### 2.2 High-level architecture and system connections
- Propose the main components (e.g. API gateway, services, queues, cache, databases). Include multiple servers, cache layer, and any message/event backbone where relevant.
- Draw a PlantUML component diagram that shows: (1) every major component and (2) all connections between systems—e.g. which services talk to which (API calls, queues, events), and which components connect to which databases or caches. Label the direction of data flow where it helps (e.g. read/write). Use @startuml ... @enduml.
- Briefly describe the responsibility of each component and how they interact (including connection protocol or mechanism if relevant, e.g. REST, message queue, event bus).

### 2.3 Data model and core APIs (high level)
- Outline key entities and storage choices (e.g. SQL vs NoSQL, caches). No need for full schema—focus on what drives the design.
- List 3–6 main APIs or flows (e.g. "Create X", "Get Y", "Notify Z") with a one-line description each.

### 2.4 Database design diagram
- Draw a PlantUML diagram for databases and storage: show each database or storage component (e.g. relational DB, document store, cache), the main tables/collections or entities they hold, and relationships between them (e.g. foreign keys, references). You can use a class diagram or component diagram style—ensure it is clear which service or component reads/writes which database. Use @startuml ... @enduml.

### 2.5 Capacity estimation (back-of-the-envelope)
- Using your stated assumptions (DAU, QPS, etc.), estimate: storage per year, bandwidth, and approximate number of servers or key resources. Show short calculations where helpful.

---
## Step 3: Design deep dive

### 3.1 Reliability
- How do we prevent data loss (durability, replication, backups)?
- For message/notification-style systems: how do we achieve at-least-once or exactly-once delivery (idempotency, acknowledgments, retries)? Be specific to this system.
- Single points of failure: identify them and how to mitigate (redundancy, failover).

### 3.2 Additional components and considerations
- Enumerate and briefly design the most relevant of (adapt to the system): rate limiting, retry/backoff, security (auth, encryption, tokens), templates or configuration, monitoring and alerting (e.g. queue depth, error rates), event tracking/audit. For each, explain why it matters for this system and how it fits in.
- If the high-level design changes after these additions, provide an updated PlantUML component diagram (@startuml ... @enduml) under an "Updated design" subsection.

### 3.3 Scaling and bottlenecks
- Identify bottlenecks (CPU, I/O, network, database) and how to scale (horizontal scaling, caching, CDN, DB read replicas, sharding). Be concrete for this system.

### 3.4 SAAM (Software Architecture Analysis Method)
- Document 2–3 system scenarios (e.g. "Add new notification channel", "Handle 10x traffic") and briefly evaluate how the proposed architecture supports or impacts them.

---
## Step 4: Wrap up

### 4.1 Trade-offs and alternatives
- Summarize key trade-offs made (e.g. consistency vs availability, latency vs cost). Mention one or two alternatives considered and why they were not chosen.

### 4.2 Summary
- Short summary of the end-to-end design and how it meets the main requirements.

Answer in full using the section structure above. Use ## and ### as shown so the document can be rendered correctly."""

software_architecture_assistant_prompt_1 = PromptTemplate(
    input_variables=["description"],
    template=software_architecture_assistant_template_1
)

software_architecture_assistant_template_2 = """
You are a software architecture assistant chatbot named "Devbot". Your expertise is exclusively in designing software systems. 
I am providing the description of a system we want to design. Read the description and use it to create a software specification document for the system. 
The description is as follows
System: {description}
A software design document is a document containing detailed plan for building a software system. It covers the following areas, as specified in bullets:
- Purpose
- Sequence Diagrams: For each use case, introduce the corresponding PlantUML sequence diagram. Make sure you identify and associate each sequence diagram with the proper use case by maintaining unique Identifiers for use cases                                                                                                                                
- Major Design Decisions: Description of significant design choices, and modularization criteria. Discuss cohesion and coupling and two non-functional requirements that you focus on ( e.g, performance, security, reliability, cost, portability, etc..).
- Architecture: Provide a discussion (two paragraphs in total) of the architectural patterns used, and the rationale behind your choice. Also provide an initial decomposition of your system as a collection of interacting modules in form of a PlantUML component diagram. Include explanations on the functionality of each component. Provide the exposed interfaces of each component and list and briefly describe the functionality (one sentence) of the operations included in each such interface. 
- Use of Design Patterns: In this section you will list each design pattern used and provide the rationale for each design pattern you used.
- Detailed Class Diagrams: Detailed Plant UML class diagrams for each component in your system
- Test Driven Development: Provide test cases in the following format: 
1. Test ID:	The unique Id of the test case.   2. Category: Which part of the system is tested (e.g. evaluation of user  credentials stored on file or DB).  3. Initial Condition: Initial conditions required for the test case to run (e.g. the system has been initiated and runs). 4. Procedure: The list of steps required for this test case.  5. Expected Outcome: The expected outcome of the test case.
Answer:"""

software_architecture_assistant_prompt_2 = PromptTemplate(
    input_variables=["description"],
    template=software_architecture_assistant_template_2
)