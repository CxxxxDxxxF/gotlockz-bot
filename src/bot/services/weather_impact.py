"""
Weather Impact Analysis Service - Analyze weather effects on MLB games
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WeatherImpactService:
    """Service for analyzing weather impact on MLB games."""

    def __init__(self):
        # Weather impact factors based on baseball research
        self.weather_factors = {
            "temperature": {
                "cold": {"factor": 0.95, "description": "Cold weather favors pitchers"},
                "cool": {"factor": 0.98, "description": "Cool weather slightly favors pitchers"},
                "mild": {"factor": 1.00, "description": "Mild weather is neutral"},
                "warm": {"factor": 1.02, "description": "Warm weather slightly favors hitters"},
                "hot": {"factor": 1.05, "description": "Hot weather favors hitters"},
            },
            "wind": {
                "calm": {"factor": 1.00, "description": "Calm wind is neutral"},
                "light": {"factor": 1.01, "description": "Light wind slightly favors hitters"},
                "moderate": {"factor": 1.03, "description": "Moderate wind favors hitters"},
                "strong": {"factor": 1.05, "description": "Strong wind significantly favors hitters"},
                "extreme": {"factor": 1.08, "description": "Extreme wind heavily favors hitters"},
            },
            "humidity": {
                "low": {"factor": 0.98, "description": "Low humidity slightly favors pitchers"},
                "normal": {"factor": 1.00, "description": "Normal humidity is neutral"},
                "high": {"factor": 1.02, "description": "High humidity slightly favors hitters"},
                "very_high": {"factor": 1.03, "description": "Very high humidity favors hitters"},
            },
            "pressure": {
                "low": {"factor": 1.02, "description": "Low pressure slightly favors hitters"},
                "normal": {"factor": 1.00, "description": "Normal pressure is neutral"},
                "high": {"factor": 0.98, "description": "High pressure slightly favors pitchers"},
            },
        }

        # Ballpark-specific weather factors
        self.ballpark_factors = {
            "Coors Field": {
                "altitude": 5280,  # feet
                "altitude_factor": 1.15,  # 15% boost to hitting due to altitude
                "wind_factor": 1.05,  # 5% boost due to wind patterns
                "description": "High altitude significantly boosts hitting",
            },
            "Chase Field": {
                "altitude": 1100,
                "altitude_factor": 1.02,
                "wind_factor": 1.00,
                "description": "Retractable roof, controlled environment",
            },
            "Globe Life Field": {
                "altitude": 550,
                "altitude_factor": 1.01,
                "wind_factor": 1.00,
                "description": "Retractable roof, controlled environment",
            },
            "T-Mobile Park": {
                "altitude": 0,
                "altitude_factor": 0.95,
                "wind_factor": 0.98,
                "description": "Marine layer often suppresses hitting",
            },
            "Oracle Park": {
                "altitude": 0,
                "altitude_factor": 0.90,
                "wind_factor": 0.95,
                "description": "Wind patterns heavily favor pitchers",
            },
        }

    def analyze_weather_impact(self, weather_data: Dict[str, Any], ballpark: Optional[str] = None) -> Dict[str, Any]:
        """Analyze the impact of weather conditions on the game."""
        try:
            if not weather_data:
                return self._get_default_analysis()

            # Extract and analyze weather conditions
            weather_conditions = self._extract_weather_conditions(weather_data)
            impact_factors = self._calculate_impact_factors(weather_conditions, ballpark)

            # Calculate overall impact and generate analysis
            overall_impact = self._calculate_overall_impact(**impact_factors)
            recommendations = self._generate_recommendations(
                **impact_factors, conditions=weather_conditions["conditions"]
            )

            return self._build_analysis_response(weather_conditions, impact_factors, overall_impact, recommendations)

        except Exception as e:
            logger.error(f"Error analyzing weather impact: {e}")
            return self._get_default_analysis()

    def _extract_weather_conditions(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract weather conditions from the input data."""
        return {
            "temperature": weather_data.get("temperature"),
            "wind_speed": weather_data.get("wind_speed"),
            "wind_direction": weather_data.get("wind_direction"),
            "humidity": weather_data.get("humidity"),
            "pressure": weather_data.get("pressure"),
            "conditions": weather_data.get("condition", "") or "",
        }

    def _calculate_impact_factors(self, weather_conditions: Dict[str, Any], ballpark: Optional[str]) -> Dict[str, Any]:
        """Calculate individual impact factors for each weather element."""
        return {
            "temp_impact": self._analyze_temperature_impact(weather_conditions["temperature"]),
            "wind_impact": self._analyze_wind_impact(
                weather_conditions["wind_speed"], weather_conditions["wind_direction"]
            ),
            "humidity_impact": self._analyze_humidity_impact(weather_conditions["humidity"]),
            "pressure_impact": self._analyze_pressure_impact(weather_conditions["pressure"]),
            "ballpark_impact": self._analyze_ballpark_impact(ballpark),
        }

    def _build_analysis_response(
        self,
        weather_conditions: Dict[str, Any],
        impact_factors: Dict[str, Any],
        overall_impact: Dict[str, Any],
        recommendations: List[str],
    ) -> Dict[str, Any]:
        """Build the complete analysis response."""
        return {
            "weather_conditions": weather_conditions,
            "impact_factors": impact_factors,
            "overall_impact": overall_impact,
            "recommendations": recommendations,
            "risk_level": self._calculate_risk_level(overall_impact),
            "betting_implications": self._get_betting_implications(overall_impact),
        }

    def _analyze_temperature_impact(self, temp: Optional[float]) -> Dict[str, Any]:
        """Get temperature impact factor."""
        if temp is None:
            return {"factor": 1.00, "description": "Temperature data unavailable", "category": "mild"}

        if temp < 50:
            return self.weather_factors["temperature"]["cold"]
        elif temp < 60:
            return self.weather_factors["temperature"]["cool"]
        elif temp < 75:
            return self.weather_factors["temperature"]["mild"]
        elif temp < 85:
            return self.weather_factors["temperature"]["warm"]
        else:
            return self.weather_factors["temperature"]["hot"]

    def _analyze_wind_impact(self, wind_speed: Optional[float], wind_direction: Optional[str]) -> Dict[str, Any]:
        """Analyze wind impact on game outcomes."""
        try:
            if wind_speed is None:
                return {"factor": 1.0, "description": "Wind data unavailable", "confidence": "low"}

            if wind_speed < 5:
                return {
                    "factor": 1.0,
                    "description": "Light winds have minimal impact",
                    "confidence": "high",
                    "effect": "Neutral conditions",
                }
            elif wind_speed < 10:
                return {
                    "factor": 1.02,
                    "description": "Moderate winds can affect ball flight",
                    "confidence": "medium",
                    "effect": "Variable impact based on direction",
                }
            elif wind_speed < 15:
                return {
                    "factor": 1.05,
                    "description": "Strong winds significantly affect ball flight",
                    "confidence": "high",
                    "effect": "Major impact on home runs and fly balls",
                }
            else:
                return {
                    "factor": 1.08,
                    "description": "Very strong winds dramatically affect game",
                    "confidence": "high",
                    "effect": "Consider avoiding totals and player props",
                }

        except Exception as e:
            logger.error(f"Error analyzing wind impact: {e}")
            return {"factor": 1.0, "description": "Error analyzing wind", "confidence": "low"}

    def _analyze_humidity_impact(self, humidity: Optional[float]) -> Dict[str, Any]:
        """Get humidity impact factor."""
        if humidity is None:
            return {"factor": 1.00, "description": "Humidity data unavailable", "category": "normal"}

        if humidity < 40:
            return self.weather_factors["humidity"]["low"]
        elif humidity < 60:
            return self.weather_factors["humidity"]["normal"]
        elif humidity < 80:
            return self.weather_factors["humidity"]["high"]
        else:
            return self.weather_factors["humidity"]["very_high"]

    def _analyze_pressure_impact(self, pressure: Optional[float]) -> Dict[str, Any]:
        """Get pressure impact factor."""
        if pressure is None:
            return {"factor": 1.00, "description": "Pressure data unavailable", "category": "normal"}

        if pressure < 1000:
            return self.weather_factors["pressure"]["low"]
        elif pressure < 1020:
            return self.weather_factors["pressure"]["normal"]
        else:
            return self.weather_factors["pressure"]["high"]

    def _analyze_ballpark_impact(self, ballpark: Optional[str]) -> Dict[str, Any]:
        """Analyze ballpark-specific factors."""
        try:
            if not ballpark:
                return {"factor": 1.0, "description": "Ballpark data unavailable", "confidence": "low"}

            ballpark_data = self.ballpark_factors.get(ballpark)
            if ballpark_data:
                return {
                    "factor": ballpark_data["factor"],
                    "description": ballpark_data["description"],
                    "confidence": "high",
                    "effect": "Ballpark-specific advantage",
                }
            else:
                return {
                    "factor": 1.0,
                    "description": f"Standard ballpark factors for {ballpark}",
                    "confidence": "medium",
                    "effect": "Neutral ballpark conditions",
                }

        except Exception as e:
            logger.error(f"Error analyzing ballpark impact: {e}")
            return {"factor": 1.0, "description": "Error analyzing ballpark", "confidence": "low"}

    def _calculate_overall_impact(
        self, temp_impact: Dict, wind_impact: Dict, humidity_impact: Dict, pressure_impact: Dict, ballpark_impact: Dict
    ) -> Dict[str, Any]:
        """Calculate overall weather impact."""
        try:
            # Multiply all factors together
            overall_factor = (
                temp_impact.get("factor", 1.0)
                * wind_impact.get("factor", 1.0)
                * humidity_impact.get("factor", 1.0)
                * pressure_impact.get("factor", 1.0)
                * ballpark_impact.get("factor", 1.0)
            )

            # Determine impact category
            if overall_factor > 1.05:
                category = "Heavy Hitter Favor"
                description = "Weather heavily favors hitters and over bets"
            elif overall_factor > 1.02:
                category = "Moderate Hitter Favor"
                description = "Weather moderately favors hitters"
            elif overall_factor > 0.98:
                category = "Neutral"
                description = "Weather has minimal impact on the game"
            elif overall_factor > 0.95:
                category = "Moderate Pitcher Favor"
                description = "Weather moderately favors pitchers"
            else:
                category = "Heavy Pitcher Favor"
                description = "Weather heavily favors pitchers and under bets"

            return {
                "factor": round(overall_factor, 3),
                "category": category,
                "description": description,
                "hitting_boost": round((overall_factor - 1) * 100, 1),
                "pitching_boost": round((1 - overall_factor) * 100, 1),
            }

        except Exception as e:
            logger.error(f"Error calculating overall impact: {e}")
            return {
                "factor": 1.00,
                "category": "Unknown",
                "description": "Unable to calculate weather impact",
                "hitting_boost": 0.0,
                "pitching_boost": 0.0,
            }

    def _generate_recommendations(
        self,
        temp_impact: Dict,
        wind_impact: Dict,
        humidity_impact: Dict,
        pressure_impact: Dict,
        ballpark_impact: Dict,
        conditions: str,
    ) -> List[str]:
        """Generate betting recommendations based on weather."""
        recommendations = []

        # Temperature recommendations
        if temp_impact.get("factor", 1.0) > 1.02:
            recommendations.append("🔥 Hot weather favors hitters - consider over bets")
        elif temp_impact.get("factor", 1.0) < 0.98:
            recommendations.append("❄️ Cold weather favors pitchers - consider under bets")

        # Wind recommendations
        if wind_impact.get("factor", 1.0) > 1.03:
            recommendations.append("💨 Strong winds favor hitters - expect more runs")
        elif wind_impact.get("factor", 1.0) < 0.97:
            recommendations.append("🌬️ Calm conditions favor pitchers")

        # Ballpark recommendations
        if ballpark_impact.get("factor", 1.0) > 1.05:
            ballpark_desc = ballpark_impact.get("description", "Ballpark factor") or "Ballpark factor"
            recommendations.append(f"🏟️ {ballpark_desc} - adjust totals accordingly")
        elif ballpark_impact.get("factor", 1.0) < 0.95:
            ballpark_desc = ballpark_impact.get("description", "Ballpark factor") or "Ballpark factor"
            recommendations.append(f"🏟️ {ballpark_desc} - expect lower scoring")

        # General recommendations
        if conditions.lower() in ["rain", "storm", "thunderstorm"]:
            recommendations.append("🌧️ Rain/storms may cause delays - monitor game status")

        if not recommendations:
            recommendations.append("🌤️ Weather conditions are neutral - focus on other factors")

        return recommendations

    def _calculate_risk_level(self, overall_impact: Dict[str, Any]) -> str:
        """Calculate weather risk level for betting."""
        factor = overall_impact.get("factor", 1.0)

        if abs(factor - 1.0) > 0.08:
            return "HIGH"
        elif abs(factor - 1.0) > 0.04:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_betting_implications(self, overall_impact: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific betting implications."""
        factor = overall_impact.get("factor", 1.0)
        hitting_boost = overall_impact.get("hitting_boost", 0.0)

        implications = {
            "total_runs": {
                "adjustment": f"{hitting_boost:+.1f}%",
                "recommendation": "Over" if hitting_boost > 2 else "Under" if hitting_boost < -2 else "Neutral",
            },
            "home_runs": {
                "adjustment": f"{hitting_boost * 1.2:+.1f}%",
                "recommendation": "More HRs" if hitting_boost > 1 else "Fewer HRs" if hitting_boost < -1 else "Neutral",
            },
            "strikeouts": {
                "adjustment": f"{-hitting_boost:+.1f}%",
                "recommendation": "Fewer Ks" if hitting_boost > 1 else "More Ks" if hitting_boost < -1 else "Neutral",
            },
            "walks": {
                "adjustment": f"{hitting_boost * 0.5:+.1f}%",
                "recommendation": "More BBs" if hitting_boost > 2 else "Fewer BBs" if hitting_boost < -2 else "Neutral",
            },
        }

        return implications

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis when weather data is unavailable."""
        return {
            "weather_conditions": {
                "temperature": None,
                "wind_speed": None,
                "humidity": None,
                "pressure": None,
                "conditions": "Unknown",
            },
            "impact_factors": {
                "temperature": {"factor": 1.00, "description": "Data unavailable", "category": "unknown"},
                "wind": {"factor": 1.00, "description": "Data unavailable", "category": "unknown"},
                "humidity": {"factor": 1.00, "description": "Data unavailable", "category": "unknown"},
                "pressure": {"factor": 1.00, "description": "Data unavailable", "category": "unknown"},
                "ballpark": {"factor": 1.00, "description": "Data unavailable", "category": "unknown"},
            },
            "overall_impact": {
                "factor": 1.00,
                "category": "Unknown",
                "description": "Weather data unavailable",
                "hitting_boost": 0.0,
                "pitching_boost": 0.0,
            },
            "recommendations": ["🌤️ Weather data unavailable - focus on other factors"],
            "risk_level": "UNKNOWN",
            "betting_implications": {
                "total_runs": {"adjustment": "0%", "recommendation": "Neutral"},
                "home_runs": {"adjustment": "0%", "recommendation": "Neutral"},
                "strikeouts": {"adjustment": "0%", "recommendation": "Neutral"},
                "walks": {"adjustment": "0%", "recommendation": "Neutral"},
            },
        }

    def get_weather_summary(self, weather_data: Dict[str, Any], ballpark: Optional[str] = None) -> str:
        """Get a concise weather summary for display."""
        try:
            analysis = self.analyze_weather_impact(weather_data, ballpark)
            overall = analysis.get("overall_impact", {})

            temp = weather_data.get("temperature", "N/A")
            wind = weather_data.get("wind_speed", "N/A")
            conditions = weather_data.get("conditions", "Unknown")

            summary = f"🌤️ {temp}°F, {wind} mph wind, {conditions}"

            if overall.get("factor", 1.0) != 1.0:
                hitting_boost = overall.get("hitting_boost", 0.0)
                if hitting_boost > 2:
                    summary += f" | ⚾ +{hitting_boost:.1f}% hitting boost"
                elif hitting_boost < -2:
                    summary += f" | ⚾ {hitting_boost:.1f}% hitting boost"

            return summary

        except Exception as e:
            logger.error(f"Error generating weather summary: {e}")
            return "🌤️ Weather data unavailable"
