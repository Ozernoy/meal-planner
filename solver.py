from scipy.optimize import linprog

class NutritionSolver:
    def __init__(self, calorie_coeffs, protein_coeffs, fat_coeffs, carb_coeffs, calorie_goal, protein_goal, fat_goal, carb_goal):
        """
        Initializes the NutritionSolver with the coefficients for each product's nutritional values
        and the user's nutritional goals.

        :param calorie_coeffs: List of calorie values per unit of each product
        :param protein_coeffs: List of protein values per unit of each product
        :param fat_coeffs: List of fat values per unit of each product
        :param carb_coeffs: List of carbohydrate values per unit of each product
        :param calorie_goal: User's daily caloric intake goal
        :param protein_goal: User's daily protein intake goal (in grams)
        :param fat_goal: User's daily fat intake goal (in grams)
        :param carb_goal: User's daily carbohydrate intake goal (in grams)
        """
        self.calorie_coeffs = calorie_coeffs
        self.protein_coeffs = protein_coeffs
        self.fat_coeffs = fat_coeffs
        self.carb_coeffs = carb_coeffs
        self.calorie_goal = calorie_goal
        self.protein_goal = protein_goal
        self.fat_goal = fat_goal
        self.carb_goal = carb_goal

    def solve(self, unit_constraints=None):
        """
        Solves the linear programming problem to minimize the deviation from the user's nutritional goals.

        :param unit_constraints: Optional list of tuples specifying min and max units for each product
        :return: List of quantities of each product that best meet the nutritional goals
        """
        n = len(self.calorie_coeffs)
        
        # Initial decision variables for product quantities, and then deviations
        c = [0] * n  # We don't care about minimizing product quantities directly
        c += [1] * 8  # We want to minimize the sum of the 8 deviation variables
        
        # Coefficients matrix for equality constraints
        A_eq = [
            self.calorie_coeffs + [-1, 1, 0, 0, 0, 0, 0, 0],  # Calories constraint
            self.protein_coeffs + [0, 0, -1, 1, 0, 0, 0, 0],  # Protein constraint
            self.fat_coeffs + [0, 0, 0, 0, -1, 1, 0, 0],      # Fat constraint
            self.carb_coeffs + [0, 0, 0, 0, 0, 0, -1, 1],     # Carbs constraint
        ]

        # Goals (right-hand side of the equations)
        b_eq = [self.calorie_goal, self.protein_goal, self.fat_goal, self.carb_goal]

        # Default bounds for the decision variables (non-negative quantities)
        if unit_constraints is None:
            unit_constraints = [(0, None)] * n
        
        dev_bounds = [(0, None)] * 8  # Non-negativity constraint for deviations

        # Combine the bounds
        bounds = unit_constraints + dev_bounds

        # Solve the linear program
        result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        if result.success:
            return result.x[:n]  # Return only the quantities of the products
        else:
            raise ValueError("No feasible solution found.")
