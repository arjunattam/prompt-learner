from prompt_learner.adapters.openai import OpenAI
from prompt_learner.templates.openai_template import OpenAICompletionTemplate

from prompt_learner.tasks.sql_generation import SQLGenerationTask
from prompt_learner.examples.example import Example

from prompt_learner.optimizers.selectors.random_sampler import RandomSampler
from prompt_learner.prompts.cot import CoT


def execute(inputs, parameters):
    # Prepare the prompt
    sql_description = parameters.get("base_prompt", "")
    sql_task = SQLGenerationTask(description=sql_description)
    schema = """CREATE TABLE singer (
    singer_id NUMERIC PRIMARY KEY,
        name TEXT,
        country TEXT,
        song_name TEXT,
        song_release_year TEXT,
        age NUMERIC,
        is_male TIMESTAMP
    );
    """
    sql_task.add_example(
        Example(
            text="How many singers do we have?",
            context=schema,
            label="SELECT COUNT(singer_id) FROM singer;",
        )
    )
    sql_task.add_example(
        Example(
            text="What is the average, minimum, and maximum age for all French singers?",
            context=schema,
            label="SELECT AVG(age), MIN(age), MAX(age) FROM singer WHERE country='France';",
        )
    )
    task = sql_task
    openai_template = OpenAICompletionTemplate(task=sql_task)
    sampler = RandomSampler(num_samples=1, task=sql_task)
    sampler.select_examples()
    openai_prompt = CoT(template=openai_template, selector=sampler)
    openai_prompt.assemble_prompt()

    # Run the prompt
    openai_prompt.add_inference(inputs["question"], inputs["schema"])
    return {"value": task.predict(OpenAI(), openai_prompt.prompt)}