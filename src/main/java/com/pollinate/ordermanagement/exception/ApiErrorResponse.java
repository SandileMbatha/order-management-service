package com.pollinate.ordermanagement.exception;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import lombok.Builder;
import lombok.Getter;

/**
 * Standard error response structure returned by all exception handlers.
 *
 * <p>Provides a consistent API error contract with optional fields
 * for validation errors and missing resource identifiers.</p>
 */
@Getter
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiErrorResponse {

    private final LocalDateTime timestamp;
    private final int status;
    private final String error;
    private final String message;
    private final Map<String, String> fieldErrors;
    private final List<Long> missingProductIds;
}

