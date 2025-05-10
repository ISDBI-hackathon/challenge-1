from services.fas_classifier import FASClassifier

def test_fas_classifier():
    classifier = FASClassifier()
    
    # Test case 1: GreenTech buyout
    transaction1 = """
    Context: GreenTech exits in Year 3, and Al Baraka Bank buys out its stake.
    Adjustments:
    Buyout Price: $1,750,000
    Bank Ownership: 100%
    Accounting Treatment:
    Derecognition of GreenTech's equity
    Recognition of acquisition expense
    Journal Entry for Buyout:
    Dr. GreenTech Equity $1,750,000
    Cr. Cash $1,750,000
    """
    
    print("\nTest Case 1: GreenTech Buyout")
    print("=" * 50)
    weights = classifier.classify_transaction(transaction1)
    for weight in weights:
        print(f"\nStandard: {weight.standard.name}")
        print(f"Weight: {weight.weight:.2f}")
        print(f"Confidence: {weight.confidence:.2f}")
        print(f"Explanation: {weight.relevance_explanation}")
        print("\nRelevant FAS Sections:")
        for section in weight.relevant_sections:
            print(f"- {section}")
    
    # Test case 2: Ijarah MBT
    transaction2 = """
    On 1 January 2019 Alpha Islamic bank (Lessee) entered into an Ijarah MBT arrangement with
    Super Generators for Ijarah of a heavy-duty generator purchase by Super Generators at a price
    of USD 450,000. Super Generators has also paid USD 12,000 as import tax and US 30,000 for freight charges.
    The Ijarah Term is 02 years and expected residual value at the end USD 5,000. At the end of
    Ijarah Term, it is highly likely that the option of transfer of ownership of the underlying asset to
    the lessee shall be exercised through purchase at a price of USD 3,000.
    Alpha Islamic Bank will amortize the 'right of use' on yearly basis and it is required to pay yearly
    rental of USD 300,000.
    """
    
    print("\n\nTest Case 2: Ijarah MBT")
    print("=" * 50)
    weights = classifier.classify_transaction(transaction2)
    for weight in weights:
        print(f"\nStandard: {weight.standard.name}")
        print(f"Weight: {weight.weight:.2f}")
        print(f"Confidence: {weight.confidence:.2f}")
        print(f"Explanation: {weight.relevance_explanation}")
        print("\nRelevant FAS Sections:")
        for section in weight.relevant_sections:
            print(f"- {section}")
    
    # Test case 3: Murabaha
    transaction3 = """
    Al Rajhi Bank enters into a Murabaha transaction with a customer for the purchase of equipment.
    The cost price is USD 100,000, and the bank adds a profit margin of 10%.
    The total selling price is USD 110,000, payable in 12 monthly installments.
    The bank purchases the equipment and takes possession before selling it to the customer.
    """
    
    print("\n\nTest Case 3: Murabaha")
    print("=" * 50)
    weights = classifier.classify_transaction(transaction3)
    for weight in weights:
        print(f"\nStandard: {weight.standard.name}")
        print(f"Weight: {weight.weight:.2f}")
        print(f"Confidence: {weight.confidence:.2f}")
        print(f"Explanation: {weight.relevance_explanation}")
        print("\nRelevant FAS Sections:")
        for section in weight.relevant_sections:
            print(f"- {section}")

if __name__ == "__main__":
    test_fas_classifier() 