import pytest

from app.assistants.curriculum_tools.project_based_activity_expert.core import executor
from app.services.assistant_registry import Message, MessagePayload, MessageType, Role, UserInfo

base_attributes = {
    "user_info": UserInfo(
        user_name="Aaron",
        user_age=30,
        user_preference="Senior AI Engineer"
    )
}


def test_executor_translate_valid():
    result = executor(
        **base_attributes,
        messages=[
            Message(
                role=Role.human,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Suggest a group project for middle school students that fosters collaboration."
                )
            ),
            Message(
                role=Role.ai,
                type=MessageType.text,
                timestamp=None,
                payload=MessagePayload(
                    text=(
                        "Here are some ideas for science experiments that require no lab equipment:\n\n"
                        "1.  **Homemade Lava Lamps:**\n"
                        "    *   Materials: Empty plastic bottle, vegetable oil, water, food coloring, effervescent antacid tablets (like Alka-Seltzer).\n"
                        "    *   Instructions: Fill the bottle with oil and water, add food coloring, then drop in antacid tablets to create bubbling lava lamp effect.\n"
                        "2.  **Baking Soda and Vinegar Volcano:**\n"
                        "    *   Materials: Baking soda, vinegar, empty bottle or container, food coloring (optional), modeling clay or dirt (to build the volcano).\n"
                        "    *   Instructions: Create a volcano shape around the bottle, add baking soda inside, then pour in vinegar to create an eruption.\n"
                        "3.  **Density Tower:**\n"
                        "    *   Materials: Clear glass or plastic cylinder, multiple liquids with different densities (e.g., honey, corn syrup, dish soap, water, vegetable oil, rubbing alcohol).\n"
                        "    *   Instructions: Gently layer the liquids in the cylinder, starting with the most dense, to create distinct layers that demonstrate density differences.\n"
                        "4.  **Walking Water:**\n    *   Materials: Seven clear glasses or jars, paper towels, water, food coloring.\n"
                        "    *   Instructions: Arrange the glasses in a row, filling every other glass with water and food coloring. Use folded paper towels to connect the glasses, allowing the water to \"walk\" from one glass to another, mixing colors in the process.\n"
                        "5.  **Homemade Thermometer:**\n"
                        "    *   Materials: Clear plastic bottle, rubbing alcohol, water, clear straw, modeling clay, food coloring.\n"
                        "    *   Instructions: Mix equal parts alcohol and water with food coloring, fill the bottle partially, insert the straw, and seal around it with clay. Mark the liquid level and observe how it changes with temperature.\n"
                        "6.  **Egg Osmosis Experiment:**\n"
                        "    *   Materials: Raw eggs, vinegar, corn syrup, water.\n"
                        "    *   Instructions: Soak eggs in vinegar to dissolve the shell, then place them in corn syrup and water separately to observe osmosis as water moves in and out of the egg.\n"
                        "7.  **Static Electricity Balloon Experiment:**\n"
                        "    *   Materials: Balloons, wool cloth or hair, small pieces of paper.\n"
                        "    *   Instructions: Inflate a balloon and rub it against wool or hair to create static electricity, then hold it near small pieces of paper to make them stick to the balloon.\n"
                        "8.  **Crystal Geodes:**\n"
                        "    *   Materials: Eggshells, Borax, hot water, food coloring, glue.\n"
                        "    *   Instructions: Mix Borax with hot water, add food coloring, and pour the mixture into halved eggshells lined with glue. Allow crystals to grow over several days.\n"
                        "9.  **Paper Airplane Aerodynamics:**\n"
                        "    *   Materials: Paper, ruler, scissors (optional).\n"
                        "    *   Instructions: Experiment with different paper airplane designs, measure flight distances, and modify designs to optimize aerodynamic performance.\n"
                        "10. **Seed Germination Experiment:**\n"
                        "    *   Materials: Seeds (beans, peas, or radish seeds work well), paper towels, plastic bags or jars, water.\n"
                        "    *   Instructions: Place seeds between moist paper towels inside plastic bags or jars, observe germination over several days, and document the growth process."
                    )
                )
            ),
            Message(
                role=Role.human,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Please, summarize what you said and translate that to Spanish"
                )
            )
        ]
    )
    assert isinstance(result, str)


def test_executor_translate_invalid():
    with pytest.raises(TypeError) as exc_info:
        executor(
            messages=[
                {
                    "role": "human",
                    "type": "text",
                    "timestamp": "string",
                    "payload": {
                        "text": "Suggest a group project for middle school students that fosters collaboration."
                    }
                },
                {
                    "role": "ai",
                    "type": "text",
                    "timestamp": None,
                    "payload": {
                        "text": "Here are some ideas for science experiments that require no lab equipment:\n\n"
                                "1.  **Homemade Lava Lamps:**\n"
                                "    *   Materials: Empty plastic bottle, vegetable oil, water, food coloring, effervescent antacid tablets (like Alka-Seltzer).\n"
                                "    *   Instructions: Fill the bottle with oil and water, add food coloring, then drop in antacid tablets to create bubbling lava lamp effect.\n"
                                "2.  **Baking Soda and Vinegar Volcano:**\n"
                                "    *   Materials: Baking soda, vinegar, empty bottle or container, food coloring (optional), modeling clay or dirt (to build the volcano).\n"
                                "    *   Instructions: Create a volcano shape around the bottle, add baking soda inside, then pour in vinegar to create an eruption.\n"
                                "3.  **Density Tower:**\n"
                                "    *   Materials: Clear glass or plastic cylinder, multiple liquids with different densities (e.g., honey, corn syrup, dish soap, water, vegetable oil, rubbing alcohol).\n"
                                "    *   Instructions: Gently layer the liquids in the cylinder, starting with the most dense, to create distinct layers that demonstrate density differences.\n"
                                "4.  **Walking Water:**\n    *   Materials: Seven clear glasses or jars, paper towels, water, food coloring.\n"
                                "    *   Instructions: Arrange the glasses in a row, filling every other glass with water and food coloring. Use folded paper towels to connect the glasses, allowing the water to \"walk\" from one glass to another, mixing colors in the process.\n"
                                "5.  **Homemade Thermometer:**\n"
                                "    *   Materials: Clear plastic bottle, rubbing alcohol, water, clear straw, modeling clay, food coloring.\n"
                                "    *   Instructions: Mix equal parts alcohol and water with food coloring, fill the bottle partially, insert the straw, and seal around it with clay. Mark the liquid level and observe how it changes with temperature.\n"
                                "6.  **Egg Osmosis Experiment:**\n"
                                "    *   Materials: Raw eggs, vinegar, corn syrup, water.\n"
                                "    *   Instructions: Soak eggs in vinegar to dissolve the shell, then place them in corn syrup and water separately to observe osmosis as water moves in and out of the egg.\n"
                                "7.  **Static Electricity Balloon Experiment:**\n"
                                "    *   Materials: Balloons, wool cloth or hair, small pieces of paper.\n"
                                "    *   Instructions: Inflate a balloon and rub it against wool or hair to create static electricity, then hold it near small pieces of paper to make them stick to the balloon.\n"
                                "8.  **Crystal Geodes:**\n"
                                "    *   Materials: Eggshells, Borax, hot water, food coloring, glue.\n"
                                "    *   Instructions: Mix Borax with hot water, add food coloring, and pour the mixture into halved eggshells lined with glue. Allow crystals to grow over several days.\n"
                                "9.  **Paper Airplane Aerodynamics:**\n"
                                "    *   Materials: Paper, ruler, scissors (optional).\n"
                                "    *   Instructions: Experiment with different paper airplane designs, measure flight distances, and modify designs to optimize aerodynamic performance.\n"
                                "10. **Seed Germination Experiment:**\n"
                                "    *   Materials: Seeds (beans, peas, or radish seeds work well), paper towels, plastic bags or jars, water.\n"
                                "    *   Instructions: Place seeds between moist paper towels inside plastic bags or jars, observe germination over several days, and document the growth process."
                    }
                },
                {
                    "role": "human",
                    "type": "text",
                    "timestamp": "string",
                    "payload": {
                        "text": "Please, summarize what you said and translate that to spanish"
                    }
                }
            ]
        )
    assert isinstance(exc_info.value, TypeError)
