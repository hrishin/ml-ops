Feature: Iris Flower Classification API
  As a user of the ML API
  I want to classify iris flowers based on their measurements
  So that I can identify the species of iris flowers

  Background:
    Given the ML model is trained and available

  Scenario: Successful prediction for Setosa
    When I provide the following measurements:
      | sepal_length | sepal_width | petal_length | petal_width |
      | 5.1          | 3.5         | 1.4          | 0.2         |
    And I send a prediction request
    Then I should receive a successful response
    And the prediction should be "setosa"
    And the model version should be available in the response

  Scenario: Successful prediction for Versicolor
    When I provide the following measurements:
      | sepal_length | sepal_width | petal_length | petal_width |
      | 6.4          | 3.2         | 4.5          | 1.5         |
    And I send a prediction request
    Then I should receive a successful response
    And the prediction should be "versicolor"

  Scenario: Successful prediction for Virginica
    When I provide the following measurements:
      | sepal_length | sepal_width | petal_length | petal_width |
      | 7.7          | 3.0         | 6.1          | 2.3         |
    And I send a prediction request
    Then I should receive a successful response
    And the prediction should be "virginica"

  Scenario: Invalid request with negative values
    When I provide the following measurements:
      | sepal_length | sepal_width | petal_length | petal_width |
      | -1.0         | 3.5         | 1.4          | 0.2         |
    And I send a prediction request
    Then I should receive an error response
    And the error message should mention "Measurement must be positive"

  Scenario: Health check indicates model is loaded
    When I check the API health status
    Then the health check should report "healthy"
    And the model version should be available in the response
