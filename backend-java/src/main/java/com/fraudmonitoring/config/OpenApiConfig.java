package com.fraudmonitoring.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI fraudMonitoringOpenAPI() {
        return new OpenAPI()
                .info(new Info().title("Fraud Monitoring API")
                        .description("API for Expense & Fraud Monitoring Agent")
                        .version("v1.0.0")
                        .license(new License().name("Apache 2.0").url("http://springdoc.org")));
    }
}
