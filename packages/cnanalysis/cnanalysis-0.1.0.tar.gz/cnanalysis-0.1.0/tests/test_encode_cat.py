import pandas as pd
from cnanalysis import EncodeCat

def test_encode_cat_methods():
    # Sample DataFrame
    df = pd.DataFrame({
        'color': ['red', 'green', 'blue', 'green', 'red'],
        'size': ['S', 'M', 'L', 'M', 'S']
    })

    print("Original DataFrame:")
    print(df)

    # 1️⃣ Label Encoding
    encoder_label = EncodeCat(data=df.copy(), cat_cols=['color'], method='label')
    encoded_label = encoder_label.encode()
    print("\nLabel Encoded DataFrame:")
    print(encoded_label)

    # 2️⃣ One-Hot Encoding
    encoder_onehot = EncodeCat(data=df.copy(), cat_cols=['color'], method='onehot', drop_first=True)
    encoded_onehot = encoder_onehot.encode()
    print("\nOne-Hot Encoded DataFrame:")
    print(encoded_onehot)

    # 3️⃣ Ordinal Encoding
    ordinal_mapping = {'size': ['S', 'M', 'L']}
    encoder_ordinal = EncodeCat(data=df.copy(), cat_cols=['size'], method='ordinal', ordinal_mapping=ordinal_mapping)
    encoded_ordinal = encoder_ordinal.encode()
    print("\nOrdinal Encoded DataFrame:")
    print(encoded_ordinal)

# Run manually for inspection
if __name__ == "__main__":
    test_encode_cat_methods()

