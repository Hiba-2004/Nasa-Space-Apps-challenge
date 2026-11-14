from backend.app.database import Base, SessionLocal, engine
from backend.app.services.simulation import seed_synthetic_scenario


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        result = seed_synthetic_scenario(db)
    print(
        "Synthetic scenario ready:",
        result.astronaut_id,
        f"({result.astronauts_created} astronaut, "
        f"{result.measurements_created} measurements, {result.checkins_created} check-in created)",
    )


if __name__ == "__main__":
    main()

