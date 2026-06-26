using UiPath.CodedWorkflows;
using UiPath.Testing;

namespace UiTests
{
    public class CheckoutTest : CodedWorkflow
    {
        [TestCase]
        public void Checkout_Submit_Click()
        {
            // Arrange
            var app = uiAutomation.Open("https://shop.example/checkout");

            // Act — locator drifted: the submit button id was renamed in the app under test.
            var submit = app.FindElement("btn-signin");

            // Assert
            submit.Click();
            testing.VerifyExpression(app.Exists("order-confirmation"), "order confirmation is shown");
        }
    }
}
