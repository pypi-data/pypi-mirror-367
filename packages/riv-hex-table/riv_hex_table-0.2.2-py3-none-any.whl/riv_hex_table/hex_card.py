from IPython.display import display, HTML

class StyledHexCardGenerator:
    """
    A class to generate and display a styled HTML card.
    """
    def __init__(self, card_name: str, card_value: str, has_card_percent: bool = False, 
                 card_percent_value: str = "", card_background_color: str = "#f0f0f0",
                 info_html: str = ""):
        """
        Initializes the StyledHexCardGenerator with the card details.

        Args:
            card_name (str): The name or title of the card.
            card_value (str): The main value to display on the card.
            has_card_percent (bool): If True, a percentage value will be displayed. Defaults to False.
            card_percent_value (str): The percentage value to display. Only used if has_card_percent is True.
                                      Defaults to an empty string.
            card_background_color (str): The background color for the card container. Defaults to a light grey.
            info_html (str): HTML content for the info button tooltip. Defaults to an empty string.
        """
        self.card_name = card_name
        self.card_value = card_value
        self.has_card_percent = has_card_percent
        self.card_percent_value = card_percent_value
        self.card_background_color = card_background_color
        self.info_html = info_html

    def display_card(self):
        """
        Generates the complete HTML for the styled card and displays it using IPython.display.
        """
        # Base HTML template for the card
        html_card_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic Card</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            color: #333;
            transition: background-color 0.3s ease, color 0.3s ease;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        .container {{ 
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            width: 500px;
            border: 1px solid #777;
            transition: transform 0.3s ease-in-out;
            position: relative;
        }}

        .container:hover {{ 
            transform: translateY(-5px);
        }}

        .header {{ 
            background-color: {card_bg_color};
            color: white;
            padding: 16px 20px;
            font-weight: 500;
            font-size: 1.1em;
            height: 50px;
            display: flex;
            justify-content: center; /* Centered card name */
            align-items: center;
            position: relative; /* For absolute positioning of the info button */
        }}
        
        .header .card-name {{
            text-align: center;
            flex-grow: 1; /* Allows the card name to fill available space */
        }}

        .value {{ 
            padding: 24px 20px;
            font-size: 2.2em;
            color: #777;
            text-align: center;
            font-weight: bold;
        }}

        .percent-placeholder {{ 
            font-size: 0.9em;
            color: #6c757d;
            padding: 10px 20px 20px;
            text-align: center;
            border-top: 1px solid #eee;
        }}
        
        .info-button-container {{
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
        }}

        .info-button {{
            cursor: pointer;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: white;
            color: #777;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .tooltip-container {{
            position: relative;
            display: inline-block;
        }}

        .tooltip-container .tooltip-text {{
            visibility: hidden;
            width: 250px;
            background-color: rgba(0, 0, 0, 0.8);
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            top: 100%;
            right: 0;
            margin-top: 5px;
            opacity: 0;
            transition: opacity 0.3s;
            line-height: 1.5;
            text-align: left;
        }}

        .tooltip-container:hover .tooltip-text {{
            visibility: visible;
            opacity: 1;
        }}
         
        @media (max-width: 600px) {{ 
            .container {{ 
                width: 95%;
            }}
            .value {{ 
                font-size: 1.8em;
            }}
        }} 
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="card-name">{card_name_placeholder}</span>
            {info_button_html}
        </div>
        <div class="value">{card_value_placeholder}</div>
        {percent_section}
    </div>
</body>
</html>
        """

        percent_section = ""
        if self.has_card_percent:
            percent_section = f"<div class='percent-placeholder'>{self.card_percent_value}</div>"
        else:
            percent_section = f"<div class='percent-placeholder' style='color: white;'>{'%'}</div>"
            
        info_button_html = ""
        if self.info_html:
            info_button_html = f"""
            <div class="info-button-container">
                <div class="tooltip-container info-button">
                    <svg xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 512 512">
                        <path fill="none" stroke="white" stroke-width="20" d="M256 0c70.69 0 134.69 28.66 181.02 74.98C483.34 121.3 512 185.31 512 256c0 70.69-28.66 134.7-74.98 181.02C390.69 483.34 326.69 512 256 512c-70.69 0-134.69-28.66-181.02-74.98C28.66 390.69 0 326.69 0 256c0-70.69 28.66-134.69 74.98-181.02C121.31 28.66 185.31 0 256 0z"/>
                        <path fill="black" d="M256 161.03c0-4.28.76-8.26 2.27-11.91 1.5-3.63 3.77-6.94 6.79-9.91 3-2.95 6.29-5.2 9.84-6.7 3.57-1.5 7.41-2.28 11.52-2.28 4.12 0 7.96.78 11.49 2.27 3.54 1.51 6.78 3.76 9.75 6.73 2.95 2.97 5.16 6.26 6.64 9.91 1.49 3.63 2.22 7.61 2.22 11.89 0 4.17-.73 8.08-2.21 11.69-1.48 3.6-3.68 6.94-6.65 9.97-2.94 3.03-6.18 5.32-9.72 6.84-3.54 1.51-7.38 2.29-11.52 2.29-4.22 0-8.14-.76-11.75-2.26-3.58-1.51-6.86-3.79-9.83-6.79-2.94-3.02-5.16-6.34-6.63-9.97-1.48-3.62-2.21-7.54-2.21-11.77zm13.4 178.16c-1.11 3.97-3.35 11.76 3.3 11.76 1.44 0 3.27-.81 5.46-2.4 2.37-1.71 5.09-4.31 8.13-7.75 3.09-3.5 6.32-7.65 9.67-12.42 3.33-4.76 6.84-10.22 10.49-16.31.37-.65 1.23-.87 1.89-.48l12.36 9.18c.6.43.73 1.25.35 1.86-5.69 9.88-11.44 18.51-17.26 25.88-5.85 7.41-11.79 13.57-17.8 18.43l-.1.06c-6.02 4.88-12.19 8.55-18.51 11.01-17.58 6.81-45.36 5.7-53.32-14.83-5.02-12.96-.9-27.69 3.06-40.37l19.96-60.44c1.28-4.58 2.89-9.62 3.47-14.33.97-7.87-2.49-12.96-11.06-12.96h-17.45c-.76 0-1.38-.62-1.38-1.38l.08-.48 4.58-16.68c.16-.62.73-1.04 1.35-1.02l89.12-2.79c.76-.03 1.41.57 1.44 1.33l-.07.43-37.76 124.7z"/>
                    </svg>
                    <div class="tooltip-text">
                        {self.info_html}
                    </div>
                </div>
            </div>
            """

        # Format the final HTML with dynamic content
        final_html = html_card_template.format(
            card_name_placeholder=self.card_name,
            card_value_placeholder=self.card_value,
            percent_section=percent_section,
            card_bg_color=self.card_background_color,
            info_button_html=info_button_html
        )
         
        display(HTML(final_html))