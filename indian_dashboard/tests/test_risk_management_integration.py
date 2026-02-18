"""
Integration tests for Risk Management functionality
Tests slider synchronization, metrics calculation, and validation
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def driver():
    """Setup Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_risk_management_page_loads(driver):
    """Test that risk management test page loads"""
    driver.get('file:///C:/Users/srika/Downloads/indian_dashboard/tests/test_risk_management.html')
    
    # Wait for page to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'config-risk-per-trade')))
    
    # Check that all key elements are present
    assert driver.find_element(By.ID, 'config-risk-per-trade-slider')
    assert driver.find_element(By.ID, 'config-risk-per-trade')
    assert driver.find_element(By.ID, 'config-max-positions')
    assert driver.find_element(By.ID, 'config-max-daily-loss-slider')
    assert driver.find_element(By.ID, 'config-max-daily-loss')
    assert driver.find_element(By.ID, 'risk-amount-value')
    assert driver.find_element(By.ID, 'total-risk-value')


def test_slider_synchronization(driver):
    """Test that slider and input are synchronized"""
    driver.get('file:///C:/Users/srika/Downloads/indian_dashboard/tests/test_risk_management.html')
    
    wait = WebDriverWait(driver, 10)
    slider = wait.until(EC.presence_of_element_located((By.ID, 'config-risk-per-trade-slider')))
    input_field = driver.find_element(By.ID, 'config-risk-per-trade')
    
    # Set slider value
    driver.execute_script("arguments[0].value = 2.5; arguments[0].dispatchEvent(new Event('input'));", slider)
    time.sleep(0.2)
    
    # Check input updated
    assert input_field.get_attribute('value') == '2.5'
    
    # Set input value
    driver.execute_script("arguments[0].value = 3.5; arguments[0].dispatchEvent(new Event('input'));", input_field)
    time.sleep(0.2)
    
    # Check slider updated
    assert slider.get_attribute('value') == '3.5'


def test_metrics_calculation(driver):
    """Test that risk metrics are calculated correctly"""
    driver.get('file:///C:/Users/srika/Downloads/indian_dashboard/tests/test_risk_management.html')
    
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'config-risk-per-trade')))
    
    # Set known values
    risk_input = driver.find_element(By.ID, 'config-risk-per-trade')
    max_positions = driver.find_element(By.ID, 'config-max-positions')
    stop_loss = driver.find_element(By.ID, 'config-stop-loss')
    take_profit = driver.find_element(By.ID, 'config-take-profit')
    
    driver.execute_script("""
        arguments[0].value = 2.0;
        arguments[1].value = 3;
        arguments[2].value = 1.0;
        arguments[3].value = 2.0;
        arguments[0].dispatchEvent(new Event('input'));
    """, risk_input, max_positions, stop_loss, take_profit)
    
    time.sleep(0.5)
    
    # Check metrics are displayed
    risk_amount = driver.find_element(By.ID, 'risk-amount-value').text
    total_risk = driver.find_element(By.ID, 'total-risk-value').text
    risk_reward = driver.find_element(By.ID, 'risk-reward-value').text
    
    assert risk_amount != '--'
    assert '₹' in risk_amount
    assert total_risk != '--'
    assert '₹' in total_risk
    assert risk_reward == '2.00'


def test_daily_loss_slider(driver):
    """Test max daily loss slider synchronization"""
    driver.get('file:///C:/Users/srika/Downloads/indian_dashboard/tests/test_risk_management.html')
    
    wait = WebDriverWait(driver, 10)
    slider = wait.until(EC.presence_of_element_located((By.ID, 'config-max-daily-loss-slider')))
    input_field = driver.find_element(By.ID, 'config-max-daily-loss')
    
    # Set slider value
    driver.execute_script("arguments[0].value = 5.0; arguments[0].dispatchEvent(new Event('input'));", slider)
    time.sleep(0.2)
    
    # Check input updated
    assert input_field.get_attribute('value') == '5.0'


def test_metrics_update_on_change(driver):
    """Test that metrics update when inputs change"""
    driver.get('file:///C:/Users/srika/Downloads/indian_dashboard/tests/test_risk_management.html')
    
    wait = WebDriverWait(driver, 10)
    risk_input = wait.until(EC.presence_of_element_located((By.ID, 'config-risk-per-trade')))
    
    # Get initial metric value
    initial_risk = driver.find_element(By.ID, 'risk-amount-value').text
    
    # Change risk per trade
    driver.execute_script("arguments[0].value = 5.0; arguments[0].dispatchEvent(new Event('input'));", risk_input)
    time.sleep(0.5)
    
    # Get updated metric value
    updated_risk = driver.find_element(By.ID, 'risk-amount-value').text
    
    # Values should be different
    assert initial_risk != updated_risk


def test_color_coding(driver):
    """Test that color coding is applied to metrics"""
    driver.get('file:///C:/Users/srika/Downloads/indian_dashboard/tests/test_risk_management.html')
    
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'config-risk-per-trade')))
    
    # Set values that should trigger color coding
    risk_input = driver.find_element(By.ID, 'config-risk-per-trade')
    take_profit = driver.find_element(By.ID, 'config-take-profit')
    stop_loss = driver.find_element(By.ID, 'config-stop-loss')
    
    # Set good risk/reward ratio (should be green)
    driver.execute_script("""
        arguments[0].value = 2.0;
        arguments[1].value = 4.0;
        arguments[2].value = 2.0;
        arguments[0].dispatchEvent(new Event('input'));
    """, risk_input, take_profit, stop_loss)
    
    time.sleep(0.5)
    
    # Check that risk/reward has positive class
    risk_reward_element = driver.find_element(By.ID, 'risk-reward-value')
    classes = risk_reward_element.get_attribute('class')
    
    # Should have some color class applied
    assert 'positive' in classes or 'warning' in classes or 'negative' in classes


def test_automated_tests_run(driver):
    """Test that the automated test suite runs successfully"""
    driver.get('file:///C:/Users/srika/Downloads/indian_dashboard/tests/test_risk_management.html')
    
    wait = WebDriverWait(driver, 10)
    
    # Wait for tests to run automatically
    time.sleep(1)
    
    # Check test results
    test_output = wait.until(EC.presence_of_element_located((By.ID, 'test-output')))
    output_text = test_output.text
    
    # Should show test results
    assert 'Tests:' in output_text
    assert 'passed' in output_text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
