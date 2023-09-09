import re
import string
import requests
import pandas as pd
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# Συνάρτηση ανάκτησης πληροφοριών για έναν επιστήμονα από συγκεκριμένο URL
def get_scientist_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Εξαγωγή του επωνύμου
    name = re.sub(r'\([^)]*\)', '', soup.find('span', class_='mw-page-title-main').text.strip())
    surname = name.split()[-1]

    # Εύρεση του πίνακα πληροφοριών του επιστήμονα
    infobox = soup.find('table', class_='infobox biography vcard')

    # Εξαγωγή του αριθμού των βραβείων
    awards = 0
    awards_section = soup.find('span', string=lambda text: text and 'awards' in text.lower())

    # Εξαγωγή του αριθμού των βραβείων από τον πίνακα πληροφοριών του επιστήμονα (αν υπάρχει)
    if infobox and infobox.find('th', string='Awards'):
        awards_header = infobox.find('th', string='Awards')
        awards_row = awards_header.find_parent('tr')
        awards_cell = awards_row.find('td')
        if awards_cell.find_all('li'):
            awards = len(awards_cell.find_all('li'))
        else:
            awards = len(awards_cell.find_all('a', attrs={'title': True}))
    # Διαφορετικά εξαγωγή του αριθμού των βραβείων από το αντίστοιχο section της σελίδας
    elif awards_section:
        awards_list = awards_section.find_next('ul').find_all('li')
        awards += len(awards_list)

    # Εξαγωγή κειμένου εκπαίδευσης
    education = ''
    # Εξαγωγή αναφορών άρθρου
    for tag in soup.find_all(class_="reference"):
        tag.decompose()
    education_section = soup.find('span', string=lambda text: text and 'education' in text.lower(), attrs={'id': True})
    # Εύρεση του section της σελίδας που αναφέρεται στην εκπαίδευση του επιστήμονα
    if education_section:
        education_list = []
        sibling = education_section.find_next()
        while sibling and sibling.name not in ['h2', 'h3']:
            if sibling.name == 'p':
                education_list.append(sibling.text.strip())
            sibling = sibling.find_next()
        education = ' '.join(education_list)

    return surname, awards, education


# Συνάρτηση ανάκτησης όλων των URLs των επιστημόνων από τη σελίδα της Wikipedia
def get_urls():
    url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Εύρεση των ετικετών <span> που το κείμενό τους είναι κεφαλαίος χαρακτήρας
    span_tags = soup.find_all("span", string=lambda text: text and text in list(string.ascii_uppercase))

    href_list = []
    for span in span_tags:
        ul_parent = span.find_next("ul")
        if ul_parent:
            # Εύρεση όλων των <li> ετικετών μέσα στην <ul>
            list_items = ul_parent.find_all("li")
            for item in list_items:
                # Εύρεση της ετικέτας <a> μέσα στη <li>
                anchor = item.find_next("a")
                # Αν υπάρχει, εξαγωγή του συνδέσμου href και προσθήκη στη λίστα των URLs
                if anchor:
                    href = 'https://en.wikipedia.org' + anchor.get("href")
                    href_list.append(href)

    return href_list

# Συνάρτηση επεξεργασίας κειμένου εκπαίδευσης επιστημόνων
def stemming_and_stopwords(df):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    df.loc[:, 'education'] = df['education'].apply(lambda doc: ' '.join([stemmer.stem(w) for w in doc.split() if w not in stop_words]))


if __name__ == '__main__':
    scientists = get_urls()  # ανάκτηση των URLs όλων των επιστημόνων

    data_for_df = []    # δημιουργία λίστας για αποθήκευση δεδομένων για το DataFrame

    # Συλλογή πληροφοριών για όλους τους επιστήμονες
    for scientist in scientists:
        surname, awards, education = get_scientist_info(scientist)

        # Αν η εκπαίδευση δεν είναι κενό string, πρόσθεσε τα δεδομένα στη λίστα
        if education:
            data_for_df.append([surname, awards, education])
    
    # Δημιουργία dataframe για τα ανακτηθέντα δεδομένα
    df = pd.DataFrame(data_for_df, columns=['surname', 'awards', 'education'])

    # Ανάγνωση του αρχείου corrections.txt για εφαρμογή διορθώσεων πάνω στο dataframe σχετικά με τον αριθμό βραβείων
    # Κάθε γραμμή του αρχείου αποτελείται από τουλάχιστον δύο στοιχεία χωρισμένα με κόμμα, που είναι το επώνυμο
    # του επιστήμονα και ο σωστός αριθμός βραβείων. Αν υπάρχει και τρίτο στοιχείο, τότε πρόκειται για το index του row
    # που πρόκειται να γίνει η αλλαγή (το επώνυμο δεν αρκεί στην περίπτωση επιστημόνων με το ίδιο επώνυμο)

    corrections = {}
    with open('corrections.txt', 'r', encoding='utf-8') as corrections_file:
        for line in corrections_file:
            if line.strip().count(',') == 2:    # γραμμή με row index
                surname, num_awards, row_index = line.strip().split(',')
                row_index = int(row_index)
                corrections[(surname, row_index)] = int(num_awards)
            else:
                surname, num_awards = line.strip().split(',')
                corrections[surname] = int(num_awards)

    # Εφαρμογή των διορθώσεων στο dataframe
    for index, row in df.iterrows():
        surname = row['surname']
        if (surname, index) in corrections:
            df.at[index, 'awards'] = corrections[(surname, index)]
        elif surname in corrections:
            df.at[index, 'awards'] = corrections[surname]

    df = df.query("surname not in ['Ng', 'Zadeh']")     # αφαίρεση εγγραφών
    df = df.reset_index(drop=True)

    stemming_and_stopwords(df)
    
    # Εγγραφή δεδομένων σε αρχείο CSV, περιλαμβάνοντας μόνο τις επιθυμητές στήλες
    df[['surname', 'awards', 'education']].to_csv('scientists_data.csv', index=False)

    print("CSV file created successfully!")
