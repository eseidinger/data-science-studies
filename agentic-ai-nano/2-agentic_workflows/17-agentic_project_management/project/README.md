# Explanation of the knowledge transfer object

The **`KnowledgeTransfer`** object in `agentic_workflow.py` serves as a **shared state container** that enables communication and knowledge sharing between different agents in the workflow.

## Purpose

It acts as a centralized repository that stores and provides access to:

- **Product specification** (given initially)
- **User stories** (created by Product Manager)
- **Product features** (created by Program Manager)
- **Engineering tasks** (created by Development Engineer)

## Key Components

### Knowledge Getter Methods

These methods provide context-specific knowledge to each agent:

1. **`get_product_manager_knowledge()`** - Returns product specification and current user stories to help the Product Manager generate and refine user stories based on product requirements.

2. **`get_program_manager_knowledge()`** - Returns user stories to help the Program Manager group them into cohesive features.

3. **`get_dev_engineer_knowledge()`** - Returns user stories, product features and current engineering tasks to help the Development Engineer identify and refine specific implementation tasks.

### Setter Methods

- **`set_user_stories()`** - Called by the Product Manager Evaluation Agent to persist finalized user stories after evaluation
- **`set_product_features()`** - Called by the Program Manager Evaluation Agent to persist finalized product features after evaluation
- **`set_engineering_tasks()`** - Called by the Development Engineer Evaluation Agent to persist finalized engineering tasks after evaluation

## How It's Used in the Workflow

1. **Initialization**: A single instance `knowledge_transfer` is created at the module level, initialized with the product specification.

2. **Agent Configuration**: Agents reference the knowledge getter methods via the `knowledge_getter` parameter:

   ```python
   product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
       openai_api_key,
       persona_product_manager,
       knowledge_product_manager,
       knowledge_getter=knowledge_transfer.get_product_manager_knowledge
   )
   ```

3. **Output Persistence**: Evaluation agents use setter methods via the `output_setter` parameter to store finalized outputs:

   ```python
   product_manager_evaluation_agent = EvaluationAgent(
       openai_api_key,
       product_manager_persona_eval,
       product_manager_evaluation_criteria,
       worker_agent=product_manager_knowledge_agent,
       max_interactions=10,
       output_setter=knowledge_transfer.set_user_stories
   )
   ```

4. **Relevant knowledge sharing**: As the workflow progresses, later agents can access relevant work from earlier agents.

## Design Pattern Benefits

This design pattern enables **incremental building and distribution of relevant knowledge**:

- Each agent adds to the shared understanding
- Subsequent agents benefit from relevant previous work
- No need for explicit parameter passing between agents

## Example Flow

1. Product Manager accesses product specification via `get_product_manager_knowledge()` → creates user stories → stored via `set_user_stories()`
2. Product Manager accesses product specification and current user stories via `get_product_manager_knowledge()` → refines user stories → stored via `set_user_stories()`
3. Program Manager accesses user stories via `get_program_manager_knowledge()` → creates features → stored via `set_product_features()`
4. Development Engineer accesses user stories and product features via `get_dev_engineer_knowledge()` → creates tasks → stored via `set_engineering_tasks()`
5. Development Engineer accesses user stories, product features and engineering tasks via `get_dev_engineer_knowledge()` → refines tasks → stored via `set_engineering_tasks()`
