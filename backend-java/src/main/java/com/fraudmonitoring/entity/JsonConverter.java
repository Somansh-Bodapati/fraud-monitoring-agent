package com.fraudmonitoring.entity;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

import java.util.List;
import java.util.Map;

@Converter
public class JsonConverter implements AttributeConverter<Object, String> {
    
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Override
    public String convertToDatabaseColumn(Object attribute) {
        if (attribute == null) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(attribute);
        } catch (Exception e) {
            throw new RuntimeException("Error converting to JSON", e);
        }
    }
    
    @Override
    public Object convertToEntityAttribute(String dbData) {
        if (dbData == null || dbData.isEmpty()) {
            return null;
        }
        try {
            // Try to parse as Map first
            try {
                return objectMapper.readValue(dbData, new TypeReference<Map<String, Object>>() {});
            } catch (Exception e) {
                // If not a Map, try List
                return objectMapper.readValue(dbData, new TypeReference<List<Object>>() {});
            }
        } catch (Exception e) {
            throw new RuntimeException("Error converting from JSON", e);
        }
    }
}

