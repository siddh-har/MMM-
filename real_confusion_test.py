import sqlite3
from sklearn.metrics import confusion_matrix, accuracy_score
import seaborn as sns
import matplotlib.pyplot as plt

print("Program Started")

# CONNECT DATABASE
conn = sqlite3.connect("instance/makemymoment.db")

cursor = conn.cursor()

# FETCH REAL HOTEL DATA
cursor.execute("SELECT * FROM hotels")

hotels = cursor.fetchall()

print("Hotels Found:", len(hotels))

# SHOW FIRST HOTEL RECORD
print("Sample Hotel Record:")
print(hotels[0])

actual = []
predicted = []

# EXAMPLE USER PREFERENCES
user_rating = 4

# LOOP THROUGH HOTELS
# LOOP THROUGH HOTELS
for hotel in hotels:

    rating = float(hotel[3])

    # ACTUAL VALUES
    if rating >= 4.2:
        actual.append(1)
    else:
        actual.append(0)

# LOOP THROUGH HOTELS
for hotel in hotels:

    rating = float(hotel[3])
    price = float(hotel[2])
    hotel_type = hotel[5]

    # ACTUAL VALUES
    if rating >= 4.2:
        actual.append(1)
    else:
        actual.append(0)

    # PREDICTED VALUES
    if (
        rating >= 4 and
        price <= 4000 and
        hotel_type == "Family"
    ):
        predicted.append(1)
    else:
        predicted.append(0)

    # PREDICTED VALUES
    price = float(hotel[2])
    hotel_type = hotel[5]

    if (
        rating >= 4 and
        price <= 4000 and
        hotel_type == "Family"
    ):
        predicted.append(1)
    else:
        predicted.append(0)

# CONFUSION MATRIX
cm = confusion_matrix(actual, predicted)

# ACCURACY
accuracy = accuracy_score(actual, predicted)

print("Accuracy:", accuracy * 100)

# DRAW GRAPH
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=['Not Recommended', 'Recommended'],
    yticklabels=['Not Recommended', 'Recommended']
)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - MMM Hotel Recommendation System")

plt.show()