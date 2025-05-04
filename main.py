import mysql.connector
import getpass
from datetime import datetime, timedelta
import os

def connect_db():
	try:
		conn = mysql.connector.connect(
			host="localhost",
			user=input("Enter username for MySQL Server: "),
			password=getpass.getpass("Enter password for MySQL Server: "),
			database="kyles_cool_gym"
		)
		if conn.is_connected():
			print("Connected to MySQL.")
			return conn
		else:
			print("Connection failed.")
			return None
	except mysql.connector.Error as err:
		print(f"MySQL Error: {err}")
		return None

def clear_screen():
	os.system('cls' if os.name == 'nt' else 'clear')

def generate_trainer_schedule(cursor):
	today = datetime.today().date()
	cursor.execute("""
			DELETE FROM trainer_schedule
			WHERE date < %s
	""", (today,))
	print("Old trainer schedules removed.")

	cursor.execute("SELECT trainer_id FROM trainer")
	trainer_ids = [row[0] for row in cursor.fetchall()]
	start_date = today

	for trainer_id in trainer_ids:
		weekday_count = 0
		day_offset = 0

		while weekday_count < 10:
			current_date = start_date + timedelta(days=day_offset)
			
			if current_date.weekday() < 5:
				weekday_count += 1
				for hour in range(9, 17, 2):
					time_str = f"{hour:02}:00:00"

					cursor.execute("""
						SELECT 1 FROM trainer_schedule
						WHERE trainer_id = %s AND date = %s AND time = %s
					""", (trainer_id, current_date, time_str))
					
					if cursor.fetchone() is None:
						cursor.execute("""
							INSERT INTO trainer_schedule 
							(trainer_id, member_id, member_book, member_cancel, date, time, booked, available)
							VALUES (%s, NULL, FALSE, FALSE, %s, %s, FALSE, TRUE)
						""", (trainer_id, current_date, time_str))
			day_offset += 1
			
	print("Trainer schedules updated for the next 10 weekdays.")

def view_members_by_status(cursor, active=True):
	status = "active" if active else "inactive"
	print(f"{status.capitalize()} Members:\n")

	cursor.execute("""
		SELECT p.id, p.name, m.gold, m.silver, m.active
		FROM person p
		JOIN member mb ON p.id = mb.member_id
		JOIN membership m ON mb.member_id = m.member_id
		WHERE m.active = %s
	""", (active,))

	members = cursor.fetchall()
	if members:
		for member in members:
			member_id, name, is_gold, is_silver, is_active = member
			if is_gold:
				membership_type = "Gold"
			elif is_silver:
				membership_type = "Silver"
			else:
				membership_type = "None"
			print(f"ID: {member_id} | Name: {name} | Type: {membership_type} | Active: {is_active}")
	else:
		print("No members found.")

def deactivate_member(cursor):
	print("Deactivating a Member")
	member_id = input("Enter the member ID to deactivate: ")

	cursor.execute("SELECT name FROM person WHERE id = %s", (member_id,))
	result = cursor.fetchone()

	if not result:
		print("Member not found.")
		return
	
	member_name = result[0]
	confirm = input(f"Are you sure you want to deactivate member '{member_name}'? (y/n): ").strip().lower()
	if confirm != 'y':
		print("Action canceled")
		return
	
	cursor.execute("""
		UPDATE membership
		SET gold = FALSE,
			silver = FALSE,
			active = FALSE,
			inactive = TRUE
		WHERE member_id = %s
	""", (member_id,))

	print(f"Member '{member_name}' marked as inactive and membership removed.")

def activate_member(cursor):
	print("Reactivating a Member")
	member_id = input("Enter the member ID to reactivate: ")

	cursor.execute("SELECT name FROM person WHERE id = %s", (member_id,))
	result = cursor.fetchone()

	if not result:
		print("Member not found.")
		return
	
	member_name = result[0]
	confirm = input(f"Are you sure you want to reactivate member '{member_name}'? (y/n): ").strip().lower()
	if confirm != 'y':
		print("Action canceled")
		return
	
	print("Select new membership type:")
	print("1. Gold")
	print("2. Silver")

	while True:
		membership_input = input("Enter your choice (1 or 2): ").strip()
		if membership_input == '1':
			gold = True
			silver = False
			break
		elif membership_input == '2':
			gold = False
			silver = True
			break
		else:
			print("Invalid selection. Please enter 1 or 2.")

	cursor.execute("""
		UPDATE membership
		SET gold = %s,
			silver = %s,
			active = TRUE,
			inactive = FALSE
		WHERE member_id = %s
	""", (int(gold), int(silver), member_id))

	print(f"Member '{member_name}' reactivated with {'Gold' if gold else 'Silver'} membership.")

def view_all_trainer_schedules(cursor):
	print("Viewing All Trainer Schedules:")

	cursor.execute("""
		SELECT
			t.trainer_id,
			p.name,
			ts.date,
			ts.time,
			ts.booked,
			ts.available
		FROM trainer_schedule ts
		JOIN trainer t ON ts.trainer_id = t.trainer_id
		JOIN person p ON t.trainer_id = p.id
		ORDER BY t.trainer_id, ts.date, ts.time					
	""")

	schedules = cursor.fetchall()

	current_trainer = None
	for trainer_id, name, date, time, booked, available in schedules:
		if current_trainer != trainer_id:
			print(f"\nTrainer: {name} (ID: {trainer_id})")
			current_trainer = trainer_id
		print(f"{date} at {time} | Booked: {booked} | Available: {available}")

def register_new_member(cursor):
	print("Register a new member")

	name = input("Enter full name: ")
	password = input("Enter password: ")
	email = input("Enter email: ")
	phone = input("Enter telephone number (e.g, $$$-$$$-$$$$) (or leave blank): ") or None

	cursor.execute("""
		INSERT INTO person (name, password, email, telephone_number)
		VALUES (%s, %s, %s, %s)
	""", (name, password, email, phone))

	cursor.execute("SELECT LAST_INSERT_ID()")
	member_id = cursor.fetchone()[0]

	cursor.execute("INSERT INTO member (member_id) VALUES (%s)", (member_id,))

	print("Select new membership type:")
	print("1. Gold")
	print("2. Silver")
	while True:
		membership_input = input("Enter your choice (1 or 2): ").strip()
		if membership_input == '1':
			gold = 1
			silver = 0
			break
		elif membership_input == '2':
			gold = 0
			silver = 1
			break
		else:
			print("Invalid selection. Please enter 1 or 2.")

	cursor.execute("""
		INSERT INTO membership (member_id, gold, silver, active, inactive)
		VALUES (%s, %s, %s, TRUE, FALSE)
	""", (member_id, gold, silver))

	print(f"Member '{name}' registered with ID {member_id}.")

def view_own_schedule(cursor, trainer_id):
	print("Your schedule (next 10 weekdays):")

	cursor.execute("""
		SELECT date, time, booked, available
		FROM trainer_schedule
		WHERE trainer_id = %s AND date >= CURDATE()
		ORDER by date, time			
	""", (trainer_id,))

	rows = cursor.fetchall()
	for date, time, booked, available in rows:
		print(f"{date} at {time} | Booked: {booked} | Available: {available}")

def mark_self_unavailable(cursor, trainer_id):
	print("Mark yourself unavailable")

	date = input("Enter the date (YYYY-MM-DD): ").strip()
	time = input("Enter the time (HH:MM:SS): ").strip()

	cursor.execute("""
		SELECT available FROM trainer_schedule
		WHERE trainer_id = %s AND date = %s AND time = %s
	""", (trainer_id, date, time))
	result = cursor.fetchone()

	if not result:
		print("No such schedule slot found.")
	elif not result[0]:
		print("This slot is already marked as unavailable.")
	else:
		cursor.execute("""
			UPDATE trainer_schedule
			SET available = FALSE,
				booked = FALSE,
				member_id = NULL,
				member_book = FALSE
			WHERE trainer_id = %s AND date = %s AND time = %s
		""", (trainer_id, date, time))
		print("You have marked yourself unavailable for that slot.")

def view_available_trainer_slots(cursor):
	print("Available Trainer Slots (Next 10 Weekdays):\n")
	
	cursor.execute("""
		SELECT ts.trainer_id, p.name, ts.date, ts.time
		FROM trainer_schedule ts
		JOIN person p ON ts.trainer_id = p.id
		WHERE ts.available = TRUE AND ts.booked = FALSE AND ts.date >= CURDATE()
		ORDER BY ts.trainer_id, ts.date, ts.time
	""")
	results = cursor.fetchall()

	if results:
		for trainer_id, name, date, time in results:
			print(f"Trainer: {name} | ID: {trainer_id} | {date} at {time}")
	else:
		print("No available trainer slots found.")

def book_trainer_slot(cursor, member_id):
	print("Book a Trainer Slot")
	trainer_id = input("Enter Trainer ID: ")
	date = input("Enter Date (YYYY-MM-DD): ")
	time = input("Enter Time (HH:MM:SS): ")

	cursor.execute("""
		SELECT available, booked FROM trainer_schedule
		WHERE trainer_id = %s AND date = %s AND time = %s
	""", (trainer_id, date, time))
	result = cursor.fetchone()

	if not result:
		print("Trainer slot not found.")
	elif not result[0] or result[1]:
		print("Slot is already booked or unavailable.")
	else:
		cursor.execute("""
			UPDATE trainer_schedule
			SET member_id = %s, booked = TRUE, available = FALSE, member_book = TRUE, member_cancel = FALSE
			WHERE trainer_id = %s AND date = %s AND time = %s
		""", (member_id, trainer_id, date, time))
		print("Timeslot booked successfully!")

def cancel_trainer_session(cursor, member_id):
	print("Cancel your Booked Trainer Session")

	cursor.execute("""
		SELECT ts.trainer_id, p.name, ts.date, ts.time
		FROM trainer_schedule ts
		JOIN person p ON ts.trainer_id = p.id
		WHERE ts.member_id = %s AND ts.date >= CURDATE()
		ORDER BY ts.date, ts.time
	""", (member_id,))

	bookings = cursor.fetchall()
	if not bookings:
		print("You have no upcoming booked sessions.")
		return
	
	print("Your booked sessions:")
	index = 1
	for row in bookings:
		trainer_id, trainer_name, date, time = row
		print(f"{index}. Trainer: {trainer_name} | {date} at {time}")
		index += 1

	choice = input("\nEnter the number of the session to cancel (or '0' to exit): ").strip()
	if not choice.isdigit() or int(choice) < 1 or int(choice) > len(bookings):
		print("Action aborted.")
		return
	
	selected = bookings[int(choice) - 1]
	trainer_id, _, date, time = selected

	cursor.execute("""
		UPDATE trainer_schedule
		SET member_id = NULL,
			booked = FALSE,
			available = TRUE,
			member_book = FALSE,
			member_cancel = TRUE
		WHERE trainer_id = %s AND member_id = %s AND date = %s AND time = %s
	""", (trainer_id, member_id, date, time))

	print("\nSession canceled successfully")

def view_membership(cursor, member_id):
	print("Membership information:")

	cursor.execute("""
		SELECT gold, silver, active, inactive
		FROM membership
		WHERE member_id = %s
	""", (member_id,))
	result = cursor.fetchone()
	
	gold, silver, active, inactive = result
	membership_type = "Gold" if gold else "Silver" if silver else "None"
	print(f"Type: {membership_type}")
	print(f"Active: {bool(active)} | Inactive: {bool(inactive)}")

def log_workout(cursor, member_id):
	print("Log a workout!!")

	date = input("Date (YYYY-MM-DD): ")
	time = input("Time (HH:MM:SS): ")
	intensity = input("Intensity? (easy/hard): ").lower()

	if intensity == "easy":
		easy = True
		hard = False
	elif intensity == "hard":
		easy = False
		hard = True
	
	cursor.execute("""
		INSERT INTO workout (member_id, member_date, member_time, easy, hard)
		VALUES (%s, %s, %s, %s, %s)
	""", (member_id, date, time, easy, hard))

	# Fetch workout_id that was just created in SQL statement above
	cursor.execute("SELECT LAST_INSERT_ID()")
	workout_id = cursor.fetchone()[0]

	type_choice = input("Type: (1) Strength, (2) Cardio (or (0) to skip): ").strip()
	if type_choice == "1":
		reps = input("Reps: ")
		rest = input("Rest Time (e.g, 60s): ")
		weight = input("Weight (e.g., 100lb): ")
		cursor.execute ("""
			INSERT INTO strength (workout_id, rest_time, reps, weight)
			VALUES (%s, %s, %s, %s)
		""", (workout_id, rest, reps, weight))
	elif type_choice == "2":
		distance = input("Distance (e.g, 1mi): ")
		duration = input("Duration (e.g, (30min or 1hr)): ")
		cursor.execute("""
			INSERT INTO cardio (workout_id, distance, duration)
			VALUES (%s, %s, %s)
		""", (workout_id, distance, duration))
	else:
		print("Skipped additional workout information.")
	print("Your workout is logged!!")

def view_workout_information(cursor, member_id):
	print("Your workout history:")

	cursor.execute("""
		SELECT workout_id, member_date, member_time, easy, hard
		FROM workout
		WHERE member_id = %s
		ORDER BY member_date DESC, member_time DESC
	""", (member_id,))
	workouts = cursor.fetchall()

	if not workouts:
		print("No logged workouts.")
		return
	
	for workout in workouts:
		workout_id, date, time, easy, hard = workout
		intensity = "Easy" if easy else "Hard" if hard else "Unknown"

		print(f"\n{date} at {time} | Intensity: {intensity}")

		cursor.execute("""
			SELECT reps, rest_time, weight
			FROM strength
			WHERE workout_id = %s
		""", (workout_id,))
		strength = cursor.fetchone()
		if strength:
			reps, rest, weight = strength
			print(f"Strength: {reps} reps, {rest} rest, {weight} weight")
			continue

		cursor.execute("""
			SELECT distance, duration
			FROM cardio
			WHERE workout_id = %s
		""", (workout_id,))
		cardio = cursor.fetchone()
		if cardio:
			distance, duration = cardio
			print(f"Cardio: {distance} distance, {duration} duration")



connection = connect_db()
clear_screen()

if connection:
	cursor = connection.cursor()
	generate_trainer_schedule(cursor)
	connection.commit()

	logged_in = False
	while not logged_in:
		user_id =input("Please enter your id: ")
		user_password =input("Please enter your password: ")

		cursor.execute (
			"SELECT name FROM person WHERE id = %s AND password = %s",
			(user_id, user_password)
		)
		user = cursor.fetchone()

		if user:
			print(f"Login successful! Welcome, {user[0]}.")

			cursor.execute("SELECT 1 FROM manager WHERE manager_id = %s", (user_id,))
			is_manager = cursor.fetchone()

			cursor.execute("SELECT 1 FROM trainer WHERE trainer_id = %s", (user_id,))
			is_trainer = cursor.fetchone()

			cursor.execute("SELECT 1 FROM member WHERE member_id = %s", (user_id,))
			is_member = cursor.fetchone()

			if is_manager:
				while True:
					clear_screen()
					logged_in = True
					print("----------Manager Menu!----------")
					print("1. View active members")
					print("2. View inactive members")
					print("3. Deactivate a member")
					print("4. Reactivate a member")
					print("5. View trainer schedule")
					print("6. Register a new member")
					print("0. Logout")

					choice = input("Enter your choice: ")
					if choice == "1":
						clear_screen()
						view_members_by_status(cursor, active=True)
						input("\nPress Enter to return to home page.")
					elif choice == "2":
						clear_screen()
						view_members_by_status(cursor, active=False)
						input("\nPress Enter to return to home page.")
					elif choice == "3":
						clear_screen()
						deactivate_member(cursor)
						connection.commit()
						input("\nPress Enter to return to home page.")
					elif choice == "4":
						clear_screen()
						activate_member(cursor)
						connection.commit()
						input("\nPress Enter to return to home page.")
					elif choice == "5":
						clear_screen()
						view_all_trainer_schedules(cursor)
						input("\nPress Enter to return to home page.")
					elif choice == "6":
						clear_screen()
						register_new_member(cursor)
						connection.commit()
						input("\nPress Enter to return to home page.")
					elif choice == "0":
						clear_screen()
						print("Logging out...")
						break
					else:
						print("Invalid choice. Try again.")
						input("Press Enter to continue...")

			elif is_trainer:
				while True:
					clear_screen()
					logged_in = True
					print("----------Trainer Menu!----------")
					print("1. View your schedule")
					print("2. Mark yourself unavailable")
					print("0. Logout")

					choice = input("Enter your choice: ")
					if choice == "1":
						clear_screen()
						view_own_schedule(cursor, user_id)
						input("\nPress Enter to return to home page.")
					elif choice == "2":
						clear_screen()
						mark_self_unavailable(cursor, user_id)
						connection.commit()
						input("\nPress Enter to return to home page.")
					elif choice == "0":
						clear_screen()
						print("Logging out...")
						break
					else:
						print("Invalid choice. Try again.")
						input("Press Enter to continue...")

			elif is_member:
				cursor.execute("SELECT active, inactive FROM membership WHERE member_id = %s", (user_id,))
				result = cursor.fetchone()
				
				if result and result[1]:
					while True:
						clear_screen()
						logged_in = True
						print("----------Inactive Member Menu----------")
						print("I'm sorry, your membership is currently inactive. In order to reactivate your membership, please speak to the manager.")
						print("1. View your membership")
						print("0. Logout")

						choice = input("Enter your choice: ")
						if choice == "1":
							clear_screen()
							view_membership(cursor, user_id)
							input("\nPress Enter to return to home page.")
						elif choice == "0":
							clear_screen()
							print("Logging out...")
							break
						else:
							print("Invalid choice. Try again.")
							input("Press Enter to continue...")
				else:
					while True:
						clear_screen()
						logged_in = True
						print("----------Member Menu!----------")
						print("1. View trainer availability")
						print("2. Book a trainer session")
						print("3. Cancel a trainer session")
						print("4. View your membership")
						print("5. Log a workout")
						print("6. View past workouts")
						print("0. Logout")

						choice = input("Enter your choice: ")
						if choice == "1":
							clear_screen()
							view_available_trainer_slots(cursor)
							input("\nPress Enter to return to home page.")
						elif choice == "2":
							clear_screen()
							book_trainer_slot(cursor, user_id)
							connection.commit()
							input("\nPress Enter to return to home page.")
						elif choice == "3":
							clear_screen()
							cancel_trainer_session(cursor, user_id)
							connection.commit()
							input("\nPress Enter to return to home page.")
						elif choice == "4":
							clear_screen()
							view_membership(cursor, user_id)
							input("\nPress Enter to return to home page.")
						elif choice == "5":
							clear_screen()
							log_workout(cursor, user_id)
							connection.commit()
							input("\nPress Enter to return to home page.")
						elif choice == "6":
							clear_screen()
							view_workout_information(cursor, user_id)
							connection.commit()
							input("\nPress Enter to return to home page.")
						elif choice == "0":
							clear_screen()
							print("Logging out...")
							break
						else:
							print("Invalid choice. Try again.")
							input("Press Enter to continue...")

		else:
			print("Invalid ID or password.")
			retry = input("Would you like to try again? (y/n): ").strip().lower()
			if retry != 'y':
				break


	cursor.close()
	connection.close()

else:
	print("Exiting due to DB connection failure.")
