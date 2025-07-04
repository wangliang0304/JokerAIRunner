# NOTE: Generated By HttpRunner v4.3.5
# FROM: .\testcases\requests.json
from httprunner import HttpRunner, Config, Step, RunRequest


class TestCaseRequests(HttpRunner):

    config = (
        Config("request methods testcase with functions")
        .variables(
            **{
                "foo1": "config_bar1",
                "foo2": "config_bar2",
                "expect_foo1": "config_bar1",
                "expect_foo2": "config_bar2",
            }
        )
        .base_url("https://postman-echo.com")
        .verify(False)
        .export(*["foo3"])
    )

    teststeps = [
        Step(
            RunRequest("get with params")
            .with_variables(
                **{
                    "foo1": "${ENV(USERNAME)}",
                    "foo2": "bar21",
                    "sum_v": "${sum_two_int(10000000, 20000000)}",
                }
            )
            .get("/get")
            .with_params(**{"foo1": "$foo1", "foo2": "$foo2", "sum_v": "$sum_v"})
            .extract()
            .with_jmespath("body.args.foo2", "foo3")
            .validate()
            .assert_equal("status_code", 200, "check status_code")
            .assert_equal("body.args.foo1", "debugtalk", "check body.args.foo1")
            .assert_equal("body.args.sum_v", "30000000", "check body.args.sum_v")
            .assert_equal("body.args.foo2", "bar21", "check body.args.foo2")
        ),
        Step(
            RunRequest("post raw text")
            .with_variables(**{"foo1": "bar12", "foo3": "bar32"})
            .post("/post")
            .with_headers(**{"Content-Type": "text/plain"})
            .with_data(
                "This is expected to be sent back as part of response body: $foo1-$foo2-$foo3."
            )
            .validate()
            .assert_equal("status_code", 200, "check status_code")
            .assert_equal(
                "body.data",
                "This is expected to be sent back as part of response body: bar12-$expect_foo2-bar32.",
                "check body.data",
            )
        ),
        Step(
            RunRequest("post form data")
            .with_variables(**{"foo2": "bar23"})
            .post("/post")
            .with_headers(**{"Content-Type": "application/x-www-form-urlencoded"})
            .with_data("foo1=$foo1&foo2=$foo2&foo3=$foo3")
            .validate()
            .assert_equal("status_code", 200, "check status_code")
            .assert_equal("body.form.foo1", "$expect_foo1", "check body.form.foo1")
            .assert_equal("body.form.foo2", "bar23", "check body.form.foo2")
            .assert_equal("body.form.foo3", "bar21", "check body.form.foo3")
        ),
    ]


if __name__ == "__main__":
    TestCaseRequests().test_start()
