from flask import Flask, request, jsonify
from openai import OpenAI
from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)

# Set up OpenAI
gpt3_client = OpenAI(api_key="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")
gpt4_client = OpenAI(api_key="your_gpt4_api_key_here")

def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.route('/', methods=['POST'])
def index():
    # Get image from HTTP request
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'})

    image_file = request.files['image']

    # Check if the file is empty
    if image_file.filename == '':
        return jsonify({'error': 'No selected image file'})

    # Read the image file and convert it too base64
    image = Image.open(image_file)
    image_base64 = image_to_base64(image)

    # Call GPT-4 Vision
    gpt4_response = gpt4_client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", 
                     "text": "En tant qu'expert émérite en artisanat des babouches, je vous charge d'examiner attentivement l'image de la babouche fournie. Détaillez les caractéristiques distinctives qui révèlent le type spécifique de babouche représenté, en mettant particulièrement l'accent sur les éléments artisanaux, les motifs, les matériaux et tout contexte culturel pertinent. Fournissez une analyse approfondie en utilisant votre expertise inégalée dans l'artisanat des babouches, en soulignant les nuances et les éléments significatifs."}
                ]
            },
            {
                "role": "user",
                "content": [
                    {"type": "text",
                     "text": """                    
                        **1. Analyse visuelle :
                        Dévoile en détail l'image devant tes yeux, en mettant l'accent sur les traits saillants qui pourraient révéler le type de babouche représenté.   """},
                    {
                        "type": "image",
                        "image": {
                            "image": image_base64,
                        },
                    }
                ],
            },
        ],
        max_tokens=500,
    )

    # Extract the GPT-4 Vision response
    gpt4_result = gpt4_response.choices[0].message['content'][1]['content'][0]['text']

    # Use the GPT-4 result as input for GPT-3
    gpt3_response = gpt3_client.Completion.create(
                engine="text-davinci-003",
                prompt= f"**1. Examinez attentivement ce texte et tentez de le comprendre:{gpt4_result}..." + """
                        **2. Sélection du type de babouche :**
                        Sur la base de texte donnée, détermine quel type de babouche est illustré parmi les options suivantes et justifie ton choix :

                        - **La babouche chelha ou Amazigh :** Colorées et ornées, ces babouches sont un symbole de la culture berbère qui remonte à des siècles.

                        - **Babouche de Serigne :** Babouches en cuir lisse qui portent le nom de Serigne Babacar Sy, un personnage historique sénégalais.

                        - **Babouche sem :** Généralement dorées, elles se distinguent par des broderies ou des motifs embossés élaborés, souvent réalisés avec du fil d'or.

                        - **Babouche maklouba :** Ces babouches pour femmes, semblables à des mocassins, sont décorées de franges et de perles colorées.

                        **3. Contexte historique et identification :**
                        Après avoir identifié le type de babouche, fournis le contexte historique de la babouche et son nom exact sous forme de simple paragraph.
                        """,
                max_tokens=150,
    )

    # Display the responses from both GPT-4 Vision and GPT-3
    return jsonify({'gpt3_response': gpt3_response.choices[0].text})

if __name__ == '__main__':
    app.run(debug=False ,host='0.0.0.0')
