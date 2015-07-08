#!/usr/bin/ruby

require 'test/unit'
require './parser'


class TestParser < Test::Unit::TestCase

  def setup
    @records = parse_log_file('test.log')
    assert_equal(@records.length, 30)
  end

  def test_mean_response
    assert_equal(mean_response(@records), 76.8)
  end

  def test_mode_response
    assert_equal(mode(@records, 'response_time'), 18)
  end

  def test_median_response
    assert_equal(median_response(@records), 36.5)
  end

  def test_mode_dyno
    assert_equal(mode(@records, 'dyno'), 'web.1')
  end

end
