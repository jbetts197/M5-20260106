from pathlib import Path
import argparse

class Calculator:
    def __init__(self, num1, num2):
        self.num1 = num1
        self.num2 = num2

    def get_sum(self):
        return self.num1 + self.num2
    
    def get_difference(self):
        return self.num1 - self.num2
    
    def get_product(self):
        return self.num1 * self.num2
    
    def get_quotient(self):
        return self.num1 / self.num2
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Provide two numbers for the calculator to process")
    parser.add_argument("--number1", required=True, help="The first number for the calc")
    parser.add_argument("--number2", required=True, help="The second number for the calc")
    args = parser.parse_args()
    calc = Calculator(num1=int(args.number1), num2=int(args.number2))
    result = calc.get_product()
    output_dir = Path("/data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "result.txt"
    output_file.write_text(f"Product: {result}\n")
    print(f"Result written to {output_file}")