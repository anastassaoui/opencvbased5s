import cv2
import base64
import os
from groq import Groq
from PIL import Image
import io
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Setup
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_image(image_path):
    """Simple image processing"""
    img = cv2.imread(image_path)

    # Check if image loaded correctly
    if img is None:
        print(f"Error: Could not open or find the image: {image_path}")
        exit(1)

    img = cv2.resize(img, (800, 600))
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode()

def analyze_workplace(image_path):
    """Analyze workplace image for Root Cause Analysis"""
    # Process image
    base64_image = process_image(image_path)

    # Send to Groq
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this workplace image for Root Cause Analysis. Identify problems, assess their severity (Critical/High/Medium/Low), determine immediate causes and potential root causes. Focus on safety hazards, operational inefficiencies, quality issues, and maintenance problems. Provide a detailed analysis with severity classifications."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }]
    )

    return response.choices[0].message.content

def generate_analysis_mindmap(analysis_text):
    """Generate PlantUML mind map documenting Root Cause Analysis findings"""

    # Ask Groq to generate PlantUML code based on the analysis
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": f"""Based on this workplace Root Cause Analysis, generate a PlantUML mind map organized by severity levels.

Analysis: {analysis_text}

Use this EXACT format with severity-based color coding:
@startmindmap
* Root Cause Analysis
**[#FF0000] Critical Issues
*** Problem: [Specific safety/operational problem]
*** Immediate Cause: [Direct cause]
*** Root Cause: [Underlying system issue]
*** Action: [Immediate intervention needed]
**[#FFA500] High Priority
*** Problem: [Significant efficiency/quality issue]
*** Immediate Cause: [Direct cause]
*** Root Cause: [Underlying system issue]
*** Action: [Priority fix needed]
**[#FFFF00] Medium Priority
*** Problem: [Moderate impact issue]
*** Immediate Cause: [Direct cause]
*** Root Cause: [Underlying system issue]
*** Action: [Scheduled improvement]
**[#00FF00] Low Priority
*** Problem: [Minor issue]
*** Immediate Cause: [Direct cause]
*** Root Cause: [Underlying system issue]
*** Action: [Future enhancement]
**[#0000FF] Monitoring Areas
*** Observation: [Potential future issue]
*** Watch For: [Warning signs]
*** Prevention: [Proactive measures]
@endmindmap

Replace placeholders with actual findings from the analysis. Use the color codes for severity: Red=Critical, Orange=High, Yellow=Medium, Green=Low, Blue=Monitoring. Return ONLY the PlantUML code, no markdown."""
        }]
    )

    return response.choices[0].message.content

def generate_improvement_wbs(analysis_text):
    """Generate PlantUML WBS diagram for Root Cause resolution project breakdown"""

    # Ask Groq to generate WBS diagram based on the analysis
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": f"""Based on this workplace Root Cause Analysis, create a PlantUML WBS (Work Breakdown Structure) for the resolution project organized by severity phases.

Analysis: {analysis_text}

Use this EXACT format and create specific tasks based on the issues identified:
@startwbs
* Root Cause Resolution Project
** Phase 1: Critical Issues (Immediate)
*** Emergency Response Actions
*** Safety Risk Mitigation
*** Operational Continuity
*** Incident Documentation
** Phase 2: High Priority Fixes (Week 1-2)
*** System Repairs
*** Process Corrections
*** Quality Improvements
*** Staff Notifications
** Phase 3: Medium Priority (Month 1-2)
*** Workflow Optimization
*** Equipment Upgrades
*** Training Programs
*** Standard Updates
** Phase 4: Low Priority (Month 3-6)
*** Efficiency Enhancements
*** Preventive Measures
*** Documentation Updates
*** Long-term Planning
** Phase 5: Prevention & Monitoring (Ongoing)
*** Root Cause Prevention
*** Regular Inspections
*** Performance Tracking
*** Continuous Improvement
@endwbs

Adjust the tasks based on the specific problems and root causes found in the analysis. Focus more detailed tasks on the higher severity issues. If critical safety issues were found, expand the emergency response section.

Return ONLY the PlantUML WBS code, no markdown, no explanation, no code blocks."""
        }]
    )

    return response.choices[0].message.content

def create_plantuml_diagram(plantuml_code, filename="5s_analysis_mindmap"):
    """Send PlantUML code to kroki.io server and save diagram image"""

    try:
        # Use kroki.io - a reliable PlantUML service
        url = "https://kroki.io/plantuml/png"

        # Send POST request with PlantUML code
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(url, data=plantuml_code, headers=headers)

        if response.status_code == 200:
            # Save the diagram image
            output_path = f"{filename}.png"
            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"5S analysis mind map saved as: {output_path}")
            return output_path
        else:
            print(f"Failed to generate diagram. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error generating PlantUML diagram: {e}")
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python analyze_5s.py <image_path>")
        exit(1)

    result = analyze_5s(sys.argv[1])
    print("=== 5S Analysis Results ===")
    print(result)
    print("\n" + "="*50)

    # Generate analysis mind map diagram
    print("Generating 5S analysis mind map...")
    mindmap_code = generate_analysis_mindmap(result)

    if mindmap_code:
        print("PlantUML mind map code generated, creating diagram...")
        mindmap_path = create_plantuml_diagram(mindmap_code, "5s_analysis_mindmap")

        if mindmap_path:
            print(f"Mind map saved: {mindmap_path}")
        else:
            print("Mind map generation failed")

        # Generate improvement WBS chart
        print("Generating improvement project breakdown (WBS)...")
        wbs_code = generate_improvement_wbs(result)

        if wbs_code:
            print("PlantUML WBS code generated, creating diagram...")
            wbs_path = create_plantuml_diagram(wbs_code, "5s_improvement_wbs")

            if wbs_path:
                print(f"WBS chart saved: {wbs_path}")
                print(f"\nComplete! You now have:")
                print(f"1. Analysis mind map: {mindmap_path}")
                print(f"2. Implementation breakdown: {wbs_path}")
            else:
                print("WBS chart generation failed, but code was created:")
                print("\n--- WBS Code ---")
                print(wbs_code)
        else:
            print("Failed to generate WBS chart code")
    else:
        print("Failed to generate mind map code")