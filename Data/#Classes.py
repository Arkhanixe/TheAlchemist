class Employee:

	raise_amount = 1.04
	number_of_emps = 0

	def __init__(self,first,last,pay):
		self.first = first
		self.last = last
		self.pay = pay
		self.email = first + "." + last + "@company.com"

		Employee.number_of_emps += 1


	def fullname(self):
		return "{} {}".format(self.first,self.last)

	def apply_raise(self):
		self.pay = int(self.pay * self.raise_amount)

	@classmethod
	def set_raise_amount(cls,amount):
		cls.raise_amount = amount

	@classmethod
	def from_string(cls, emp_str):
		first, last, pay = emp_str.split("-")
		return cls(first, last, pay)

	@staticmethod
	def is_work_day(day):
		if day.weekday() == 5 or 6:
			return False
		else:
			return True

	def __repr__(self):
		return "Employee('{}','{}','{}')".format(self.first,self.last,self.pay)

	def __str__(self):
		return "{} - {}".format(self.fullname(),self.email)

class Developer(Employee):
	raise_amount = 1.10

	def __init__(self, first, last, pay, prog_lang):
		super().__init__(first, last, pay)
		self.prog_lang = prog_lang

class Manager(Employee):

	def __init__(self, first, last, pay, employees = None):
		super().__init__(first, last, pay)
		if employees is None:
			self.employees = []
		else:
			self.employees = employees

	def add_emp(self,emp):
		if emp not in self.employees:
			self.employees.append(emp)

	def remove_emp(self,emp):
		if emp in self.employees:
			self.employees.remove(emp)

	def print_emps(self):
		for emp in self.employees:
			print("-->", emp.fullname())

emp_1 = Employee("Corey","Schafer", 50000)
emp_2 = Employee("Test","User", 60000)

dev_1 = Developer("Hiro","Arkhan", 75000, "Python")
dev_2 = Developer("Sebi","None", 90000, "Python")

mgr_1 = Manager("John","Adams", 90000, [dev_1])

"""
print(emp_1)

print(repr(emp_1))
print(str(emp_1))

"""

