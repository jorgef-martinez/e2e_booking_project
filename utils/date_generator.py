# utils/date_generator.py

from datetime import datetime, timedelta
import random

def generate_valid_dates():
    """Genera fechas válidas dentro del rango de 6 meses"""
    current_date = datetime.now()
    
    # Fecha mínima: mañana
    min_date = current_date + timedelta(days=1)
    
    # Fecha máxima: 6 meses desde hoy
    max_date = current_date + timedelta(days=180)
    
    # Generar fecha de partida aleatoria dentro del rango (dejando espacio para la fecha de retorno)
    max_departing = max_date - timedelta(days=7)  # Dejar al menos una semana para el retorno
    days_range = (max_departing - min_date).days
    
    if days_range > 0:
        random_days = random.randint(1, days_range)
        departing_date = min_date + timedelta(days=random_days)
        
        # Generar fecha de retorno (1-7 días después de la partida)
        return_range = min(7, (max_date - departing_date).days)
        if return_range > 0:
            return_days = random.randint(1, return_range)
            returning_date = departing_date + timedelta(days=return_days)
            
            return (
                departing_date.strftime("%d/%m/%Y"),
                returning_date.strftime("%d/%m/%Y")
            )
    
    # Fallback: usar fechas por defecto válidas
    default_departing = (current_date + timedelta(days=14)).strftime("%d/%m/%Y")
    default_returning = (current_date + timedelta(days=21)).strftime("%d/%m/%Y")
    return default_departing, default_returning