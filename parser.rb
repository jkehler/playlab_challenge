#!/usr/bin/ruby

require "csv"


endpoints = [
  {
    method: 'GET',
    path: '/api/users/{user_id}/count_pending_messages',
    records: []
  },
  {
    method: 'GET',
    path: '/api/users/{user_id}/get_messages',
    records: []
  },
  {
    method: 'GET',
    path: '/api/users/{user_id}/get_friends_progress',
    records: []
  },
  {
    method: 'GET',
    path: '/api/users/{user_id}/get_friends_score',
    records: []
  },
  {
    method: 'POST',
    path: '/api/users/{user_id}',
    records: []
  },
  {
    method: 'GET',
    path: '/api/users/{user_id}',
    records: []
  }
]


class LogRecord
  attr_accessor :method, :path, :dyno, :connect, :response_time

  def initialize(row)
    @method = row[3].slice(7..-1)
    @path = row[4].slice(5..-1)
    @dyno = row[7].slice(5..-1)
    @connect = row[8].slice(8..-1).sub('ms', '').to_i
    @service = row[9].slice(8..-1).sub('ms', '').to_i
    @response_time = @connect + @service
  end
end


# Returns the median response time from an array of LogRecords
def median_response(records)
  if records.length == 0
    return 0.0
  end

  records = records.sort_by {|r| r.response_time}

  if records.length % 2 == 0
    return (records[records.length / 2].response_time +
            records[records.length / 2 - 1].response_time) / 2.0
  end

  return records[records.length / 2].response_time.to_f
end


# Returns the mean response time from an array of LogRecords
def mean_response(records)
  if records.length == 0
    return 0.0
  end

  return records.map {|r| r.response_time}.reduce(:+) / records.length.to_f
end


# Returns the mode @key from an array of LogRecords
def mode(records, key)
  if records.length == 0
    return 'N/A'
  end

  counts = {}

  records.each do |r|
    if counts.has_key?(r.send(key))
      counts[r.send(key)] += 1
    else
      counts[r.send(key)] = 1
    end
  end

  # sort the counts by the key
  counts = counts.sort_by {|k, v| k}

  return counts.max_by {|k, v| v}[0]
end


# Opens and parses the log file returning an array of LogRecords
def parse_log_file(file_name)

  raise ArgumentError, "Log file does not exist." unless File.file?(file_name)

  records = []

  CSV.foreach(file_name, col_sep: " ", quote_char: "'") do |row|
    # Omit any paths that do not begin with path=/api/users
    if row[4].start_with?("path=/api/users/")
      records.push(LogRecord.new(row))
    end
  end

  return records
end


if __FILE__ == $0

  raise ArgumentError, "No log file name specified." unless ARGV.length == 1

  # Generate the Regexp objects for the enpoints. Replaces {user_id} with
  # regex [0-9]+ and adds ^ and $ to beginning and end of path
  endpoints.each do |endpoint|
    endpoint[:path_rx] = Regexp.new(
      '^' + endpoint[:path].sub(/\{user\_id\}/, '[0-9]+') + '$')
  end

  parse_log_file(ARGV[0]).each do |record|
    endpoints.each do |endpoint|
      if endpoint[:method] == record.method &&
          endpoint[:path_rx].match(record.path)
        # Record matched this endpoint. Add it to the records list
        endpoint[:records].push(record)
        # if there is a match, break to save wasted cycles since a record
        # should not match multiple endpoints
        break
      end
    end
  end

  endpoints.each do |endpoint|
    puts "Endpoint:          #{endpoint[:method]} #{endpoint[:path]}"
    puts "Called:            #{endpoint[:records].length} times"
    puts "Mean response:     #{mean_response(endpoint[:records]).round(1)} ms"
    puts "Median response:   #{median_response(endpoint[:records]).round(1)} ms"
    puts "Mode response:     #{mode(endpoint[:records], 'response_time')} ms"
    puts "Most active Dyno:  #{mode(endpoint[:records], 'dyno')}"
    puts "-------------------------------------------------------------------"
  end
end
