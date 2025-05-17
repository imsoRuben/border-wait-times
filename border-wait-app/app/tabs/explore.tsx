import React, { useEffect, useState } from 'react';
import { Text, View, ActivityIndicator, FlatList, StyleSheet, RefreshControl, TextInput } from 'react-native';
interface WaitTimeItem {
  crossing_name: string;
  port_name: string;
  border: string;
  date: string;
  time: string;
  passenger_vehicle_lanes?: {
    standard_lanes?: { delay_minutes?: number };
  };
  commercial_vehicle_lanes?: {
    standard_lanes?: { delay_minutes?: number };
  };
  pedestrian_lanes?: {
    standard_lanes?: { delay_minutes?: number };
  };
  construction_notice?: string;
}


export default function ExploreScreen() {
  const [data, setData] = useState<WaitTimeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchWaitTimes = async () => {
    try {
      setError('');
      const response = await fetch('https://border-wait-times.onrender.com/wait-times');
      const json = await response.json();
      setData(json.all_ports_summary);
    } catch (err) {
      setError('Failed to load wait times.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchWaitTimes();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchWaitTimes();
  };

  const getDelayStyle = (delay: number | undefined) => {
    if (typeof delay !== 'number') return styles.text;
    if (delay <= 10) return [styles.text, styles.short];
    if (delay >= 30) return [styles.text, styles.long];
    return styles.text;
  };

  const getDelayMessage = (delay?: number) => {
    if (delay === undefined) return null;
    return (
      <Text style={{ fontSize: 12, color: '#555' }}>
        {delay > 20 ? '📈 Longer than usual' : '📉 Shorter than usual'}
      </Text>
    );
  };

  const filteredData = data.filter(item =>
    item.crossing_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.port_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const lastUpdated = filteredData.length > 0
    ? `${filteredData[0].date} ${filteredData[0].time}`
    : '';

  const renderItem = ({ item }: { item: WaitTimeItem }) => {
    const passengerDelay = item.passenger_vehicle_lanes?.standard_lanes?.delay_minutes;
    const commercialDelay = item.commercial_vehicle_lanes?.standard_lanes?.delay_minutes;
    const pedestrianDelay = item.pedestrian_lanes?.standard_lanes?.delay_minutes;

    return (
      <View style={styles.item}>
        <Text style={styles.cornerBadge}>
          {passengerDelay && passengerDelay > 20 ? '📈' : '📉'}
        </Text>
        <Text style={styles.title}>{item.crossing_name} ({item.port_name})</Text>

        <Text style={getDelayStyle(passengerDelay)}>
          Passenger Delay: {passengerDelay ?? 'N/A'} min
        </Text>
        {passengerDelay !== undefined && (
          <Text style={passengerDelay <= 10 ? styles.short : passengerDelay >= 30 ? styles.long : styles.text}>
            {passengerDelay <= 10 && '✅ Short Delay'}
            {passengerDelay >= 30 && '🚨 Long Delay'}
          </Text>
        )}
        {getDelayMessage(passengerDelay)}

        <Text style={getDelayStyle(commercialDelay)}>
          Commercial Delay: {commercialDelay ?? 'N/A'} min
        </Text>
        {commercialDelay !== undefined && commercialDelay >= 30 && (
          <Text style={styles.long}>🚨 Long Delay</Text>
        )}
        {getDelayMessage(commercialDelay)}

        <Text style={getDelayStyle(pedestrianDelay)}>
          Pedestrian Delay: {pedestrianDelay ?? 'N/A'} min
        </Text>
        {pedestrianDelay !== undefined && pedestrianDelay >= 30 && (
          <Text style={styles.long}>🚨 Long Delay</Text>
        )}
        {getDelayMessage(pedestrianDelay)}
      </View>
    );
  };

  if (loading) {
    return <ActivityIndicator size="large" style={styles.loading} />;
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {lastUpdated ? (
        <Text style={styles.timestamp}>Last updated: {lastUpdated}</Text>
      ) : null}
      <TextInput
        style={styles.searchInput}
        placeholder="Search by port or crossing name"
        value={searchQuery}
        onChangeText={setSearchQuery}
      />
      <FlatList
        data={filteredData}
        keyExtractor={(item) => `${item.port_name}-${item.crossing_name}-${item.date}`}
        renderItem={renderItem}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
  },
  item: {
    marginBottom: 16,
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  title: {
    fontWeight: 'bold',
    fontSize: 16,
    marginBottom: 4,
  },
  short: {
    color: 'green',
    fontWeight: 'bold',
  },
  long: {
    color: 'red',
    fontWeight: 'bold',
  },
  text: {
    fontSize: 14,
  },
  error: {
    color: 'red',
    fontSize: 16,
  },
  searchInput: {
    height: 40,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    marginBottom: 16,
  },
  timestamp: {
    fontSize: 10,
    color: '#555',
    textAlign: 'right',
    marginBottom: 4,
  },
  cornerBadge: {
    position: 'absolute',
    top: 4,
    right: 8,
    fontSize: 16,
    opacity: 0.6,
    width: 20,
    textAlign: 'right',
  },
});