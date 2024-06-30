houses = {"Harry": "Gryffindor", "Draco": "Slytherin"}

houses["Hermione"] = "Gryffindor"

for name in houses:
    print(f"{name} is in house {houses[name]}")