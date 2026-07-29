package com.pollinate.ordermanagement.exception;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * Global exception handler providing consistent error responses across all endpoints.
 *
 * <p>Maps domain exceptions to appropriate HTTP status codes and returns
 * a structured {@link ApiErrorResponse} body.</p>
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final String LOG_PREFIX = "[Exception Handler] - ";

    /**
     * Handles resource not found exceptions (404).
     *
     * @param ex the exception thrown when a resource is not found
     * @return a 404 response with error details
     */
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ApiErrorResponse> handleNotFound(final ResourceNotFoundException ex) {
        log.warn("{}Resource not found: {}", LOG_PREFIX, ex.getMessage());

        final ApiErrorResponse response = ApiErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.NOT_FOUND.value())
                .error(HttpStatus.NOT_FOUND.getReasonPhrase())
                .message(ex.getMessage())
                .build();

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
    }

    /**
     * Handles invalid order exceptions when referenced products do not exist (400).
     *
     * @param ex the exception containing the list of missing product IDs
     * @return a 400 response with missing product details
     */
    @ExceptionHandler(InvalidOrderException.class)
    public ResponseEntity<ApiErrorResponse> handleInvalidOrder(final InvalidOrderException ex) {
        log.warn("{}Invalid order rejected: {}", LOG_PREFIX, ex.getMessage());

        final ApiErrorResponse response = ApiErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.BAD_REQUEST.value())
                .error("Invalid Order")
                .message(ex.getMessage())
                .missingProductIds(ex.getMissingProductIds())
                .build();

        return ResponseEntity.badRequest().body(response);
    }

    /**
     * Handles bean validation failures (400).
     *
     * @param ex the validation exception containing field-level errors
     * @return a 400 response with per-field error messages
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiErrorResponse> handleValidation(final MethodArgumentNotValidException ex) {
        final Map<String, String> fieldErrors = ex.getBindingResult().getFieldErrors().stream()
                .collect(Collectors.toMap(FieldError::getField, FieldError::getDefaultMessage, (a, b) -> a));

        final ApiErrorResponse response = ApiErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.BAD_REQUEST.value())
                .error("Validation Failed")
                .message("Request validation failed")
                .fieldErrors(fieldErrors)
                .build();

        return ResponseEntity.badRequest().body(response);
    }
}
