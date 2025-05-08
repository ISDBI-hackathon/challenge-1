# AAOIFI Accounting Entry Generator

This AI-powered system generates AAOIFI-compliant accounting entries from natural language input for Islamic finance transactions. It supports FAS standards 4, 7, 10, 28, and 32.

## Features

- Natural language processing of accounting scenarios
- AAOIFI-compliant accounting entry generation
- Detailed calculations and explanations
- Support for multiple FAS standards
- RESTful API interface

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the server:
   ```bash
   python main.py
   ```

2. The API will be available at `http://localhost:8000`

3. Send a POST request to `/generate-entries` with the following JSON structure:
   ```json
   {
     "input_text": "Your accounting scenario here...",
     "fas_standard": "FAS 4"  // or FAS 7, 10, 28, 32
   }
   ```

4. The response will include:
   - Journal entries
   - Calculations
   - Detailed explanation

## Example

Input:
```
On 1 January 2019 Alpha Islamic bank (Lessee) entered into an Ijarah MBT arrangement...
```

Output:
```json
{
  "journal_entries": [...],
  "calculations": {...},
  "explanation": "..."
}
```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Supported FAS Standards

- FAS 4: Murabaha to the Purchase Orderer
- FAS 7: Mudaraba
- FAS 10: Ijarah and Ijarah Muntahia Bittamleek
- FAS 28: Investment in Sukuk, Shares and Similar Instruments
- FAS 32: Ijarah Sukuk 