import pandas as pd
import numpy as np
import csv
import re

# Feature column -> Removed nan

def normalize_clitics(word):
    """
    Normalize clitics in a word
    """
    clitics = {
        "n't": "not",
        "'m": "am",
        "'re": "are",
        "'s": "is",
        "'d": "would",
        "'ll": "will",
        "'ve": "have"
    }
    if word.lower() in clitics:
        return clitics[word.lower()]
    else:
        return word

def normalize_apostrophes(word):
    """
    Normalize apostrophes in a word
    """
    if word.endswith("'s"):
        return word[:-2] + " 's"
    elif word.endswith("'"):
        return word[:-1] + " '"
    else:
        return word

def normalize_text(text):
    """
    Normalize clitics, apostrophes, commas, periods, and emojis in a piece of text
    """
    words = text.split()
    normalized_words = []
    for word in words:
        word = normalize_clitics(word)
        word = normalize_apostrophes(word)
        normalized_words.append(word)
    return " ".join(normalized_words)

# Define a function to remove punctuation and emojis using regular expressions
def remove_punct(text):
    """
    Remove punctuation and emojis from a piece of text using regular expressions
    """
    # Remove commas and periods
    text = re.sub(r'[,.]', '', text)
    # Remove emojis
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('s.csv')

# # Remove rows with 'none' values in any of the specified columns
# columns_with_none = ['Title', 'Location', 'Description', 'Price/night', 'Interior', 'Ratings', 'Reviews', 'Features', 'Amenities']
# df = df[~df[columns_with_none].apply(lambda row: row.astype(str).str.lower().str.contains('none')).any(axis=1)]

# Remove duplicate rows
df.drop_duplicates(inplace=True)

# Normalize the 'Description' column using the normalize_text() function
df['Description'] = df['Description'].apply(normalize_text)

# # Apply the remove_punct function to the 'Description' column
# df['Description'] = df['Description'].apply(remove_punct)
df['Price/night'] = df['Price/night'].apply(remove_punct)
# # df['Title'] = df['Title'].apply(remove_punct)
# df['Location'] = df['Location'].apply(remove_punct)
# df['Interior'] = df['Interior'].apply(remove_punct)
# df['Amenities'] = df['Amenities'].apply(remove_punct)
# df["Features"] = df["Features"].str.replace(",", "")

# Split the Location column to extract the country
df['Country'] = df['Location'].apply(lambda x: x.split(',')[-1].strip())

# Replace 'New' with the mean value of Ratings and Reviews for each Location
df['Ratings'] = df.groupby('Location')['Ratings'].apply(lambda x: x.replace('New', str(round(x[x != 'New'].astype(float).mean(), 1))))
df['Reviews'] = df.groupby('Location')['Reviews'].apply(lambda x: x.replace('New', str(round(x[x != 'New'].astype(float).mean(), 1))))

# Replace 'nan' with the mean value of Ratings and Reviews of entire country
df['Ratings'] = df.groupby('Country')['Ratings'].apply(lambda x: x.replace('nan', str(round(x[x != 'nan'].astype(float).mean(), 1))))
df['Reviews'] = df.groupby('Country')['Reviews'].apply(lambda x: x.replace('nan', str(round(x[x != 'nan'].astype(float).mean(), 1))))

# Convert Ratings and Reviews to float
df['Ratings'] = df['Ratings'].astype(float)
df['Reviews'] = df['Reviews'].astype(float).round()

# Remove rows with 'nan' values in any of the specified columns
columns_with_nan = ['Ratings', 'Reviews']
df = df[~df[columns_with_nan].apply(lambda row: row.astype(str).str.lower().str.contains('nan')).any(axis=1)]

# Convert the 'Price/night' column to a numerical data type
df['Price/night'] = pd.to_numeric(df['Price/night'], errors='coerce')

# Normalize the 'Price/night' column using decimal scaling normalization
price_col = df['Price/night']
max_price = price_col.max()
decimal_places = len(str(int(max_price)))
scaled_price_col = price_col / (10 ** decimal_places)
# df['Price/night'] = scaled_price_col
df['Normalized Price/night'] = scaled_price_col

# Normalize the 'Reviews' column using decimal scaling normalization
reviews_col = df['Reviews']
max_reviews = reviews_col.max()
decimal_places = len(str(int(max_reviews)))
scaled_reviews_col = reviews_col / (10 ** (decimal_places - 1))
df['Normalized Reviews'] = scaled_reviews_col

# Loop through each row of the dataframe
for i, row in df.iterrows():
    # Check if the "Features" value contains "New"
    if "New" in row["Features"]:
        # Get the location for this row
        location = row["Location"]
        # Filter the dataframe to only include rows with the same location
        location_df = df[df["Location"] == location]
        # Calculate the mean of each parameter for this location
        mean_values = location_df["Features"].str.extract(r"Cleanliness(\d\.\d), Accuracy(\d\.\d), Communication(\d\.\d), Location(\d\.\d), Check-in(\d\.\d), Value(\d\.\d)").astype(float).mean()
        # Replace "New" with the mean values for this location
        features = row["Features"].replace("New", "Cleanliness{:.1f}, Accuracy{:.1f}, Communication{:.1f}, Location{:.1f}, Check-in{:.1f}, Value{:.1f}".format(*mean_values))
        # Update the "Features" column for this row
        df.at[i, "Features"] = features

# Replace the Features column
df["Features"] = df["Features"].str.replace(r'(\d\.\d), (\w)', r'\1, \2', regex=True).str.replace(r'(?<=\w)(\d\.\d)', r' \1', regex=True)

# # Define a list of strings to search for in the 'Features' column
# search_strings = ['Cleanlinessnan', 'Accuracynan', 'Communicationnan', 'Locationnan', 'Check-innan', 'Valuenan']
# # Remove leading and trailing whitespace characters from the 'Features' column
# df['Features'] = df['Features'].str.strip()
# # Filter out rows with any of the search strings in the 'Features' column
# df = df[~df['Features'].str.lower().isin(search_strings)]

# Drop cleaning
df = df.drop('Country', axis=1)

# Save the normalized dataset as a new CSV file
with open('clean4.csv', 'w', newline='') as output_file:
    writer = csv.writer(output_file)
    # Write the header row to the output file
    writer.writerow(df.columns.values)
    # Write each row to the output file
    for row in df.itertuples(index=False):
        writer.writerow(row)