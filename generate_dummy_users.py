import random
import pandas as pd
from faker import Faker
from faker.providers import BaseProvider
import random
import itertools


# Custom Macedonian provider
class MacedonianProvider(BaseProvider):
    male_names = ["Petar", "Aleksandar", "Kristijan", "Stefan", "Nikola", "Filip", "David", "Mihail", "Goran"]
    female_names = ["Angela", "Ana", "Elena", "Marija", "Ivana", "Simona", "Sara", "Katerina", "Tamara", "Jovana"]

    male_surnames = ["Gjorgievski", "Petrovski", "Ristovski", "Stojanov", "Nikoloski", "Kostadinov", "Todorovski", "Spasov", "Kolevski", "Zafirovski", "Velkovski"]
    female_surnames = ["Gjorgievska", "Petrovska", "Ristovska", "Trajkovska", "Ilievska", "Ristovska", "Micevska", "Angelovska", "Bozinovska", "Krstevska", "Mitrevska"]

    def name_and_surname(self):
        if random.choice([True, False]):  # машко
            name = self.random_element(self.male_names)
            surname = self.random_element(self.male_surnames)
        else:  # женско
            name = self.random_element(self.female_names)
            surname = self.random_element(self.female_surnames)
        return name, surname
    

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------

ACTIVITIES_PATH = "data/cleaned_activities.csv"
OUTPUT_PATH = "data/dummy_users.csv"
NUM_USERS = 70
DESTINATION = "Skopje"

COORD_OFFSET_RANGE = 0.005



try:
    fake = Faker("mk_MK")
except AttributeError:
    fake = Faker()
    fake.add_provider(MacedonianProvider)

random.seed(42)  


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def load_activity_coordinates(path: str) -> list[tuple[float, float]]:

    # TODO: implement
    df = pd.read_csv(path)
    coords = list(zip(df["latitude"], df["longitude"]))
    return coords


def generate_unique_email(name: str, surname: str, used: set) -> str:

    # TODO: implement
    base = f"{name.lower()}.{surname.lower()}@example.com"
    email = base
    counter = 1
    while email in used:
        email = f"{name.lower()}.{surname.lower()}{counter}@example.com"
        counter += 1
    used.add(email)
    return email


def generate_user(activity_coords: list, used_emails: set) -> dict:
    
    provider = MacedonianProvider(fake)
    name, surname = provider.name_and_surname()
    email = generate_unique_email(name, surname, used_emails)

    lat, lng = random.choice(activity_coords)
    lat += random.uniform(-COORD_OFFSET_RANGE, COORD_OFFSET_RANGE)
    lng += random.uniform(-COORD_OFFSET_RANGE, COORD_OFFSET_RANGE)

    return {
        "name": name,
        "surname": surname,
        "email": email,
        "destination": DESTINATION,
        "latitude": lat,
        "longitude": lng,
    }


# -------------------------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------------------------

def main():
    print(f"Loading activity coordinates from {ACTIVITIES_PATH}...")
    activity_coords = load_activity_coordinates(ACTIVITIES_PATH)
    print(f"  Loaded {len(activity_coords)} coordinate pairs")

    print(f"Generating {NUM_USERS} dummy users...")
    used_emails = set()
    # users = [generate_user(activity_coords, used_emails) for _ in range(NUM_USERS)]
    all_combos = list(itertools.product(MacedonianProvider.male_names, MacedonianProvider.male_surnames)) + \
            list(itertools.product(MacedonianProvider.female_names, MacedonianProvider.female_surnames))

    random.shuffle(all_combos)
    selected_combos = all_combos[:NUM_USERS]

    users = []
    for name, surname in selected_combos:
        email = generate_unique_email(name, surname, used_emails)
        lat, lng = random.choice(activity_coords)
        lat += random.uniform(-COORD_OFFSET_RANGE, COORD_OFFSET_RANGE)
        lng += random.uniform(-COORD_OFFSET_RANGE, COORD_OFFSET_RANGE)
        users.append({
            "name": name,
            "surname": surname,
            "email": email,
            "destination": DESTINATION,
            "latitude": lat,
            "longitude": lng,
    })

    print(f"Writing output to {OUTPUT_PATH}...")
    df = pd.DataFrame(users)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"  Wrote {len(df)} users")

    print("\n--- Summary ---")
    print(f"Total users generated: {len(df)}")
    print(f"Sample names:")
    print(df[["name", "surname", "email"]].head(5).to_string(index=False))


if __name__ == "__main__":
    main()