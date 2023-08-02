
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    lsh_threshold = float(input("Εισάγετε ελάχιστο ποσοστό ομοιότητας (0 - 1): "))
    min_letter, max_letter = input("Εισάγετε διάστημα ονομάτων στη μορφή X,X: ").split(',')
    num_awards = int(input("Εισάγετε ελάχιστο αριθμό βραβείων: "))

    #print(lsh_threshold, min_letter, max_letter, num_awards)

    print("\n1. k-d tree\n2. Quad tree\n3. Range tree\n4. R-tree")
    choice = int(input("Επιλέξτε δομή: "))

