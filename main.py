from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
import matplotlib.pyplot as plt
import numpy as np
import io

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# BMI calculation function
def calculate_bmi(weight, height):
    return weight / (height ** 2)

# Function to create a half-circle gauge chart
def create_bmi_gauge(bmi):
    min_bmi, max_bmi = 10, 40
    categories = [
        (18.5, "blue"),   # Underweight
        (24.9, "green"),  # Normal weight
        (29.9, "orange"), # Overweight
        (40, "red")       # Obesity
    ]
    
    fig, ax = plt.subplots(figsize=(7, 4), subplot_kw={'projection': 'polar'})
    ax.set_theta_offset(np.pi)  # Start at the left (for a half-circle gauge)
    ax.set_theta_direction(-1)  # Counter-clockwise
    
    # Limit angle to only the upper half of the circle (0 to π)
    start_angle = 0
    for limit, color in categories:
        end_angle = (limit - min_bmi) / (max_bmi - min_bmi) * np.pi
        ax.barh(1, end_angle - start_angle, left=start_angle, height=0.5, color=color, alpha=0.7)
        start_angle = end_angle

    # Plot the BMI needle on the half-circle
    bmi_angle = (bmi - min_bmi) / (max_bmi - min_bmi) * np.pi
    ax.plot([bmi_angle, bmi_angle], [0, 1], color="black", linewidth=2)

    # Style adjustments for half-circle view
    ax.set_ylim(0, 1)
    ax.set_yticklabels([])
    ax.set_xticks([])
    plt.title(f"BMI {bmi:.1f}", pad=20)

    # Save the plot to a BytesIO object for response
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

# Route to display the HTML form
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Endpoint to calculate BMI and return half-circle gauge image
@app.post("/assess_health", response_class=StreamingResponse)
async def assess_health(request: Request):
    payload = await request.json()
    weight = payload.get("weight")
    height = payload.get("height")
    bmi = calculate_bmi(weight, height)
    image_buf = create_bmi_gauge(bmi)
    return StreamingResponse(image_buf, media_type="image/png")
