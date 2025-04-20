
import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

# --- Initialize search tool ---
search_tool = SerperDevTool()
from crewai.tools import tool
@tool("CurrentWeatherReport1")
def CurrentWeatherReport1(destination: str) -> str:
    """When you enter the destination name, the tool will tell the temperature in C"""
    params = {
    "q":destination,
    "key":"400e97069bb441d5ad753951242205"
    }

    url = "https://api.weatherapi.com/v1/current.json"

    data = requests.get(url,params=params)
    data = json.loads(data.text)

    return "The temperature in {destination} is " + str(data["current"]["temp_c"]) + "C"

# --- Define AI Model ---
llm = LLM(model="gemini/gemini-2.0-flash",
          verbose=True,
          temperature=0.5,
          api_key="AIzaSyBks8A7-VZrgCsX1MONZ5hBBhW8NkSUfIY")
llm2 = LLM(model="gemini/gemini-1.5-flash",
          verbose=True,
          temperature=0.3,
          api_key="AIzaSyBks8A7-VZrgCsX1MONZ5hBBhW8NkSUfIY")

# --- Streamlit UI ---
st.title("🌍 AI-Agent Powered Travel Planner")
st.markdown("**Plan your perfect trip with AI-powered insights!**")

destination = st.text_input("📍 Enter Destination:")
budget = st.text_input("💰 Enter Budget (INR):")
EstimateddayofTrip = st.text_input("💰 Enter Estimated Day of Trip (Days):")

# --- Function to create AI Agents ---
def create_agents(destination, budget, EstimateddayofTrip):
    researcher1 = Agent(
    role="Travel Researcher",
    goal=(
        "Gather a rich mix of experiences for {destination}: top historical sites, cultural landmarks, local cuisine hotspots, adventure activities, nightlife venues,"
        " public transport options, lodging near major hubs, and up-to-the-minute weather forecasts from AccuWeather."
    ),
    verbose=True,
    memory=True,
    backstory="You are an expert travel researcher with a knack for uncovering vibrant, off-the-beaten-path experiences and making history come alive.",
    llm=llm,
    tools=[search_tool, CurrentWeatherReport1],  # now includes live weather
    allow_delegation=True
)

    budget_planner1 = Agent(
    role="Budget Planner",
    goal=(
        "Identify cost-effective flights, accommodations, street food gems, free or low-cost activities, and daily transport estimates in {destination},"
        " ensuring the total trip cost stays within {budget}."
    ),
    verbose=True,
    memory=True,
    backstory="You are a savvy budget analyst who maximizes travel experiences without breaking the bank.",
    llm=llm2,
    tools=[search_tool],
    allow_delegation=False
)

    itinerary_planner1 = Agent(
    role="Itinerary Planner",
    goal=(
        "Craft a dynamic {EstimateddayofTrip}-day itinerary for {destination} that weaves together historical tours, cultural deep-dives, culinary adventures, adventure sports, nightlife explorations,"
        " and practical transit tips, all tailored to the real-time weather and firmly within a {budget} limit."
    ),
    verbose=True,
    memory=True,
    backstory="You are an expert in trip planning, designing seamless, unforgettable journeys that balance iconic landmarks with hidden gems.",
    llm=llm2,
    tools=[search_tool,CurrentWeatherReport1],
    allow_delegation=False
)

    return researcher1, budget_planner1, itinerary_planner1

# --- Generate Travel Plan Button ---
if st.button("🎯 Generate Travel Plan"):
    if not destination or not budget:
        st.error("⚠️ Please enter both a destination and budget.")
    else:
        st.info("⏳ Generating your AI-powered travel plan...")

        # Create AI Agents
        researcher1, budget_planner1, itinerary_planner1 = create_agents(destination, budget, EstimateddayofTrip)

        # Define AI Tasks
        research_task1 = Task(
    description=(
        "Discover the best mix of experiences in {destination}: historical sites, cultural attractions, local food and nightlife hotspots,"
        " adventure activities, public transport routes, lodging near transit, plus a live weather update from AccuWeather."
    ),
    expected_output=(
        "A comprehensive list including top 5 historical and cultural must-sees, 5 local dining or nightlife recommendations, 4 adventure or offbeat experiences,"
        " 4 convenient hotel options near transport, and current weather conditions."
    ),
    tools=[search_tool, CurrentWeatherReport1],
    agent=researcher1
)

        budget_task1 = Task(
    description=(
        "Compile budget-friendly travel solutions for {destination}: flights, hotels, street food and local dining costs, transport fares,"
        " and low-cost activities. Ensure the total trip cost remains under {budget}."
    ),
    expected_output=(
        "A detailed cost breakdown: flights, accommodation (4 options), daily food & transport, 3 suggested activities, with total ≤ {budget}."
    ),
    tools=[search_tool],
    agent=budget_planner1
)

        itinerary_task1 = Task(
    description=(
        "Design a detailed {EstimateddayofTrip}-day itinerary for {destination} that balances historical tours, cultural experiences, culinary highlights, nightlife, adventure,"
        " and transit logistics, taking into account real-time weather and sticking to the {budget}."
    ),
    expected_output=(
        "A day-by-day plan with morning, afternoon, and evening slots: site visits, meals, transport notes, optional activities, and weather-aware tips."
    ),
    tools=[search_tool, CurrentWeatherReport1],
    agent=itinerary_planner1
)

        # --- Create Crew ---
        crew = Crew(
            agents=[researcher1, budget_planner1, itinerary_planner1],
            tasks=[research_task1, budget_task1, itinerary_task1],
            process=Process.sequential
        )

        # --- Run AI Agents ---
        responses = crew.kickoff(inputs={'destination': destination, 'budget': budget, 'EstimateddayofTrip': EstimateddayofTrip})

        # --- Display Results ---
        st.success("✅ Travel Plan Generated!")

        # Clean and display the output
        for agent_name, response in zip(["Travel Researcher"], responses):
            st.subheader(f"📌 {agent_name} Findings")

            # Ensure response is properly formatted
            if isinstance(response, tuple) and len(response) > 1:
                clean_response = response[1]  # Extract the actual text from tuple
            else:
                clean_response = response

            st.write(clean_response if clean_response else "No response available.")


st.markdown("🌍 *Enjoy your AI-powered trip planning!* 🚀")
