import json

from solver import NutritionSolver


class NutritionOptimizer:
    def __init__(self, json_file):
        """
        Initializes the NutritionOptimizer with data from a JSON file.

        :param json_file: Path to the JSON file containing nutritional information.
        """
        self.json_file = json_file  # Ensure json_file is saved as an attribute
        with open(json_file, "r") as f:
            self.data = json.load(f)

        self.product_names = [product["name"] for product in self.data["products"]]
        self.calorie_coeffs = [product["calories"] for product in self.data["products"]]
        self.protein_coeffs = [product["protein"] for product in self.data["products"]]
        self.fat_coeffs = [product["fat"] for product in self.data["products"]]
        self.carb_coeffs = [product["carbs"] for product in self.data["products"]]

    def restructure_json(self, product_constraints):
        """
        Restructures the JSON data so that products in product_constraints appear first.

        :param product_constraints: Dictionary specifying min and max grams for each product
        :return: None
        """
        constrained_products = []
        other_products = []

        # Separate the products into constrained and unconstrained lists
        for product in self.data["products"]:
            if product["name"] in product_constraints:
                constrained_products.append(product)
            else:
                other_products.append(product)

        # Restructure the products list
        self.data["products"] = constrained_products + other_products

        # Write the restructured data back to the JSON file
        with open(self.json_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def optimize(
        self,
        calorie_goal,
        protein_goal,
        fat_goal,
        carb_goal,
        product_constraints=None,
        num_days=1,
    ):
        """
        Optimizes the nutrition plan based on the provided nutritional goals.

        :param calorie_goal: User's daily caloric intake goal
        :param protein_goal: User's daily protein intake goal (in grams)
        :param fat_goal: User's daily fat intake goal (in grams)
        :param carb_goal: User's daily carbohydrate intake goal (in grams)
        :param product_constraints: Optional dictionary specifying min and max grams for each product
        :param num_days: The number of days for which to multiply the daily plan (e.g., for weekly plan)
        :return: None
        """
        if product_constraints is None:
            product_constraints = {}

        # Restructure JSON data based on constraints
        self.restructure_json(product_constraints)

        # Filter out only the products with constraints
        filtered_names = []
        filtered_calorie_coeffs = []
        filtered_protein_coeffs = []
        filtered_fat_coeffs = []
        filtered_carb_coeffs = []
        unit_constraints = []

        for i, name in enumerate(self.product_names):
            if name in product_constraints:
                filtered_names.append(name)
                filtered_calorie_coeffs.append(self.calorie_coeffs[i])
                filtered_protein_coeffs.append(self.protein_coeffs[i])
                filtered_fat_coeffs.append(self.fat_coeffs[i])
                filtered_carb_coeffs.append(self.carb_coeffs[i])
                min_val, max_val = product_constraints[name]
                unit_constraints.append((min_val / 100, max_val / 100))

        solver = NutritionSolver(
            filtered_calorie_coeffs,
            filtered_protein_coeffs,
            filtered_fat_coeffs,
            filtered_carb_coeffs,
            calorie_goal,
            protein_goal,
            fat_goal,
            carb_goal,
        )

        quantities = solver.solve(unit_constraints)
        self.output(
            quantities,
            filtered_names,
            calorie_goal,
            protein_goal,
            fat_goal,
            carb_goal,
            num_days,
        )

    def output(
        self,
        quantities,
        filtered_names,
        calorie_goal,
        protein_goal,
        fat_goal,
        carb_goal,
        num_days=1,
    ):
        """
        Outputs the optimized nutrition plan, including detailed nutritional information
        and deviations from the target goals.

        :param quantities: List of quantities in units (where 1 unit = 100 grams)
        :param filtered_names: List of product names that were considered in the solver
        :param calorie_goal: User's daily caloric intake goal
        :param protein_goal: User's daily protein intake goal (in grams)
        :param fat_goal: User's daily fat intake goal (in grams)
        :param carb_goal: User's daily carbohydrate intake goal (in grams)
        :param num_days: Number of days for the multi-day meal plan (default: 1)
        :return: None
        """
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0

        print("Optimized daily nutrition plan:")
        for i, quantity in enumerate(quantities):
            if quantity == 0:
                continue  # Skip products with 0 quantity
            grams = quantity * 100  # Convert to grams
            print(f"{filtered_names[i]}: {grams:.0f} grams")
            total_calories += self.calorie_coeffs[i] * quantity
            total_protein += self.protein_coeffs[i] * quantity
            total_fat += self.fat_coeffs[i] * quantity
            total_carbs += self.carb_coeffs[i] * quantity

        # Calculate deviations
        cal_dev = total_calories - calorie_goal
        prot_dev = total_protein - protein_goal
        fat_dev = total_fat - fat_goal
        carb_dev = total_carbs - carb_goal

        print("\nTotal Daily Nutritional Information:")
        print(f"Calories: {total_calories:.2f} kcal (Deviation: {cal_dev:+.2f} kcal)")
        print(f"Protein: {total_protein:.2f} g (Deviation: {prot_dev:+.2f} g)")
        print(f"Fat: {total_fat:.2f} g (Deviation: {fat_dev:+.2f} g)")
        print(f"Carbohydrates: {total_carbs:.2f} g (Deviation: {carb_dev:+.2f} g)")

        # Weekly or multi-day plan
        print(f"\nOptimized meal plan for {num_days} days:")
        for i, quantity in enumerate(quantities):
            if quantity == 0:
                continue  # Skip products with 0 quantity
            grams = (
                quantity * 100 * num_days
            )  # Convert to grams and multiply by number of days
            print(f"{filtered_names[i]}: {grams:.0f} grams for {num_days} days")


def test_nutrition_optimizer():
    optimizer = NutritionOptimizer(r"data.json")

    # Define hardcoded constraints (in grams) for some products
    product_constraints = {
        "Chicken Breasts": (300, 300),
        "Oatmeal": (0, 100),
        "Buckwheat": (160, 200),
        "FiberPowder": (0, 60),
        "WheyProtein": (30, 90),
        "Milk": (0, 1200),
        "Almonds": (10, 20),
        "Oil": (10, 50),
        "Tomatoes": (100, 200),
        "Bell Peppers": (150, 300),
        "Eggs": (0, 150),
    }

    optimizer.optimize(
        calorie_goal=2802,
        protein_goal=160,
        fat_goal=93,
        num_days=4,  # Example: Calculate for 5 days
        carb_goal=300,
        product_constraints=product_constraints,
    )


# Run the test function
test_nutrition_optimizer()
