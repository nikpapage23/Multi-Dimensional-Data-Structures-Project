import time
import random
from main import main_app
import matplotlib.pyplot as plt

# Λεξικό για αποθήκευση των χρόνων εκτέλεσης κάθε δομής/επιλογής
execution_times = {choice: [] for choice in range(1, 5)}

# Για κάθε μία από τις 4 επιλογές: τρέχουμε 10 φορές τη συνάρτηση main_app
# δίνοντας κάθε φορά διαφορετικές-τυχαίες εισόδους.
for i in range(10):
    min_letter = chr(random.randint(ord('A'), ord('Y')))    # τυχαίος χαρακτήρας στο διάστημα [A, Y]
    # τυχαίος χαρακτήρας στο διάστημα [min_letter + 1, Z]
    max_letter = chr(random.randint(ord(min_letter) + 1, ord('Z')))
    letter_range = min_letter + ',' + max_letter
    num_awards = random.randint(0, 6)  # τυχαίος ακέραιος αριθμός στο διάστημα [0, 6]
    lsh_threshold = round(random.uniform(0.4, 0.65), 2)  # τυχαίος δεκαδικός αριθμός στο διάστημα [0.4, 0.7]

    for choice in range(1, 5):
        print(letter_range, num_awards, lsh_threshold, choice)
        start_time = time.time()    # ξεκίνημα χρονομέτρησης
        main_app(lsh_threshold, min_letter, max_letter, num_awards, choice)
        end_time = time.time()      # τέλος χρονομέτρησης
        diff = end_time - start_time    # υπολογισμός διάρκειας

        # Αποθήκευση του χρόνου εκτέλεσης στο λεξικό
        execution_times[choice].append(diff)

# Υπολογισμός των μέσων χρόνων εκτέλεσης για κάθε δομή/επιλογή
average_times = {choice: sum(times)/len(times) for choice, times in execution_times.items()}

# Plot των αποτελεσμάτων
choices = ['k-d tree + LSH', 'Quad tree + LSH', 'Range tree + LSH', 'R-tree + LSH']
avg_times = list(average_times.values())

plt.figure(figsize=(8, 6))

plt.bar(choices, avg_times)
plt.xlabel('Data Structure')
plt.ylabel('Average Execution Time (seconds)')
plt.title('Average Execution Time for each Data Structure')
plt.xticks(choices)
plt.show()
