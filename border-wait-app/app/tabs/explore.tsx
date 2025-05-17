import React, { useEffect, useState } from 'react';
import { Text, View, ActivityIndicator, FlatList, StyleSheet, RefreshControl } from 'react-native';

export default function ExploreScreen() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

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

  const getDelayStyle = (delay: number | string | undefined) => {
    if (typeof delay !== 'number') return styles.text;
    if (delay <= 10) return [styles.text, styles.short];
    if (delay >= 30) return [styles.text, styles.long];
    return styles.text;
  };

  const renderItem = ({ item }) => (
    <View style={styles.item}>
      <Text style={styles.title}>{item.crossing_name} ({item.port_name})</Text>
      <Text style={getDelayStyle(item.passenger_vehicle_lanes?.standard_lanes?.delay_minutes)}>
        Passenger Delay: {item.passenger_vehicle_lanes?.standard_lanes?.delay_minutes || 'N/A'} min
      </Text>
      <Text style={getDelayStyle(item.commercial_vehicle_lanes?.standard_lanes?.delay_minutes)}>
        Commercial Delay: {item.commercial_vehicle_lanes?.standard_lanes?.delay_minutes || 'N/A'} min
      </Text>
      <Text style={getDelayStyle(item.pedestrian_lanes?.standard_lanes?.delay_minutes)}>
        Pedestrian Delay: {item.pedestrian_lanes?.standard_lanes?.delay_minutes || 'N/A'} min
      </Text>
    </View>
  );

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
    <FlatList
      data={data}
      keyExtractor={(item) => `${item.port_name}-${item.crossing_name}`}
      renderItem={renderItem}
      contentContainerStyle={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    />
  );
}

const styles = StyleSheet.create({
  container: {
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
});