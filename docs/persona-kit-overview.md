## **1. Core Mission & Philosophy**

**PersonaKit** is a service for enabling AI systems to deeply understand and model specific human individuals for complex collaborative and coaching workflows.

Its purpose is to move beyond generic roles and model an individual’s unique preferences, communication style, motivations, and work patterns. This allows AI and human collaborators to interact with greater effectiveness, precision, and empathy.

## **2. The Core Architectural Concepts**

The system is built on a strict separation of concerns between key entities:

* **Observations:** The raw data layer. This includes all ingested source material, whether stored directly or as pointers to external data.  
* **Mindscape (The Terrain):** A private, comprehensive database of derived traits and vector embeddings, synthesized from user-approved **Observations**. The data within is tagged by volatility to support efficient retrieval.  
* **Persona Mapper (The Cartographer):** A configuration-driven, versioned definition of *how to create a Persona*. It consists of declarative rules in YAML/JSON that define conditions and actions for mapping the Mindscape to a specific purpose. These configurations can be automatically adjusted based on feedback.  
* **Persona (The Map):** A durable, context-specific reference model of an individual. It is composed of two parts to balance performance and freshness:  
  * **Persona Core:** A pre-computed, cached foundation containing low-volatility, foundational traits (e.g., core beliefs, communication style). This is the system's "materialized view."  
  * **Contextual Overlay:** A lightweight, dynamically-fetched layer containing high-volatility, just-in-time information (e.g., current availability, recent sentiment).  
* **Actor (The Traveler):** An external agent that **takes on** a Persona to inform its actions. The Actor uses the Persona as its map to navigate a task and **can optionally provide** feedback on the map's accuracy.

## **3. The Persona Lifecycle & System Flow**

The framework operates in a continuous cycle of data ingestion, analysis, and system improvement.

### **Phase 1: The ETL Pipeline (Building the Mindscape)**

* **Goal:** To build and maintain the rich, derived data store for each individual through an intentional, user-controlled ETL (Extract, Transform, Load) process.  
* **Process:**  
  1. **Extract:** Connectors gather Observations and place them in a private **Curation Workbench**. The user approves the relevant Observations for processing.  
  2. **Transform:** A background **Mindscaper agent** processes the approved Observations. Using a meta-model of **volatility heuristics**, it derives traits and **tags each insight** (e.g., as volatility: low for a core belief, or volatility: high for a temporary state).  
  3. **Load:** The Mindscaper loads this tagged, transformed data into the appropriate store (Document or Vector) within the **Mindscape**.

### **Phase 2: Persona Mapping (Generating the Persona)**

* **Goal:** To assemble the right "map" for the specific "journey" an Actor is about to undertake.  
* **Process:** This on-demand process is triggered by an API call from an Actor.  
  * GET /map-persona?mapperId=...\&personaId=...\&detailLevel=...  
* **Key Components:**  
  1. **The Persona Mapper:** The Actor specifies which mapper to use.  
  2. **Detail Levels (User Budget Control):** The Actor selects a level (Instant, Balanced, Deep Dive).  
  3. **Hybrid Retrieval Pipeline:**  
     * The system retrieves the cached **Persona Core**. If it's stale (based on significant changes to low-volatility data), it can be rebuilt according to the selected Detail Level.  
     * The system performs a fast, dynamic query to fetch the **Contextual Overlay** from the high-volatility data in the Mindscape.  
     * The Core and Overlay are combined into a single Persona object and returned to the Actor.

### **Phase 3: The Feedback Loop (Improving Mapper Configurations)**

* **Goal:** To enable the service to learn from real-world outcomes, making the mapper configurations more accurate over time.  
* **Process:**  
  1. **Action & Observation:** An Actor uses a generated Persona to perform a task.  
  2. **Submit Feedback:** The Actor (or a human supervisor) submits feedback via the POST /feedback endpoint.  
  3. **Asynchronous Refinement:** A background **Configuration Adjuster** analyzes feedback associated with specific rules in the Persona Mapper configuration.  
  4. **Automatic Weight Adjustment:** The system adjusts rule weights and thresholds in the mapper configuration based on feedback patterns, creating a new version of the configuration automatically.

## **4. Next Steps**

For detailed technical implementation specifications, including system architecture, data synchronization protocols, concurrency handling, and API endpoints, see the [PersonaKit Technical Specification](persona-kit-technical-spec.md).