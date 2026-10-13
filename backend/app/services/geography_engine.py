from __future__ import annotations
from typing import Any, Dict, List, Optional

class GeographyEngine:
    """
    Global Trade Geography Engine.
    Handles the hierarchy: World -> Country -> State -> City -> Port/Airport.
    """

    # Mock database of geographic hierarchy
    # In production, this would be a SQL DB with tables for countries, states, cities, etc.
    DATA = {
        "India": {
            "states": {
                "Karnataka": {
                    "cities": {
                        "Bengaluru": {
                            "ports": ["Bengaluru International Airport (BLR)", "Bengaluru Inland Container Depot"],
                        },
                        "Mangaluru": {
                            "ports": ["New Mangalore Port (NMP)"],
                        },
                        "Mysuru": {
                            "ports": ["Mysuru Inland Port"],
                        }
                    }
                },
                "Maharashtra": {
                    "cities": {
                        "Mumbai": {
                            "ports": ["Nhava Sheva (JNPT)", "Mumbai Port Trust"],
                        },
                        "Pune": {
                            "ports": ["Pune Inland Port"],
                        }
                    }
                },
                "Gujarat": {
                    "cities": {
                        "Mundra": {
                            "ports": ["Mundra Port"],
                        },
                        "Kandla": {
                            "ports": ["Kandla Port"],
                        }
                    }
                }
            }
        },
        "United States": {
            "states": {
                "California": {
                    "cities": {
                        "Los Angeles": {
                            "ports": ["Port of Los Angeles", "LAX Airport"],
                        },
                        "San Francisco": {
                            "ports": ["Port of Oakland", "SFO Airport"],
                        }
                    }
                },
                "New York": {
                    "cities": {
                        "New York City": {
                            "ports": ["Port of New York and New Jersey", "JFK Airport", "LGA Airport"],
                        }
                    }
                },
                "Texas": {
                    "cities": {
                        "Houston": {
                            "ports": ["Port of Houston", "IAH Airport"],
                        }
                    }
                }
            }
        },
        "Germany": {
            "states": {
                "Bavaria": {
                    "cities": {
                        "Munich": {
                            "ports": ["Munich Airport (MUC)"],
                        }
                    }
                },
                "Berlin": {
                    "cities": {
                        "Berlin": {
                            "ports": ["BER Airport"],
                        }
                    }
                }
            }
        },
        "China": {
            "states": {
                "Guangdong": {
                    "cities": {
                        "Shenzhen": {
                            "ports": ["Port of Shenzhen"],
                        },
                        "Guangzhou": {
                            "ports": ["Port of Guangzhou"],
                        }
                    }
                },
                "Shanghai": {
                    "cities": {
                        "Shanghai": {
                            "ports": ["Port of Shanghai", "PVG Airport"],
                        }
                    }
                }
            }
        }
    }

    def get_countries(self) -> List[str]:
        return sorted(list(self.DATA.keys()))

    def get_states(self, country: str) -> List[str]:
        country_data = self.DATA.get(country)
        if not country_data:
            return []
        return sorted(list(country_data.get("states", {}).keys()))

    def get_cities(self, country: str, state: str) -> List[str]:
        try:
            cities = self.DATA[country]["states"][state]["cities"]
            return sorted(list(cities.keys()))
        except KeyError:
            return []

    def get_ports(self, country: str, state: str, city: str) -> List[str]:
        try:
            ports = self.DATA[country]["states"][state]["cities"][city]["ports"]
            return sorted(ports)
        except KeyError:
            return []

    def validate_route(self, origin: Dict[str, str], destination: Dict[str, str]) -> bool:
        # Verify that the provided hierarchy exists in our data
        def check(route):
            c = route.get("country")
            s = route.get("state")
            ci = route.get("city")
            p = route.get("port")
            if not c or c not in self.DATA: return False
            if s and s not in self.DATA[c]["states"]: return False
            if ci and s and ci not in self.DATA[c]["states"][s]["cities"]: return False
            if p and s and ci and p not in self.DATA[c]["states"][s]["cities"][ci]["ports"]: return False
            return True

        return check(origin) and check(destination)

geography_engine = GeographyEngine()
