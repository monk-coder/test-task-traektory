import argparse

from src.services import check_slot, find_free_slots, find_slot, show_busy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--check-slot", type=str, help="Date and time slot to check. Use format 'YYYY-MM-DD HH:MM-HH:MM'"
    )
    parser.add_argument("-b", "--show-busy", action="store_true", help="Show all busy slots.")
    parser.add_argument(
        "-f", "--find-free-slot", type=str, help="Find a free slot at a certain date. Use format 'YYYY-MM-DD"
    )
    parser.add_argument(
        "-d", "--find-suitable-slots", type=str, help="Find free slots for a specific duration. Use format 'HH:MM'"
    )
    args = parser.parse_args()

    if args.check_slot:
        check_slot(args.check_slot)

    if args.show_busy:
        show_busy()

    if args.find_free_slot:
        find_free_slots(args.find_slot)

    if args.find_suitable_slots:
        find_slot(args.find_suitable_slots)


if __name__ == "__main__":
    main()
