import java.io.IOException;
import java.util.Map;
import java.util.TreeMap;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class TopNMovies {
    public static class TopNMapper extends Mapper<Object, Text, NullWritable, Text> {
        private TreeMap<Double, String> topMovies = new TreeMap<>();
        private final int N = 10;
        private final int MIN_VOTES = 1000;

        public void map(Object key, Text value, Context context) {
            String line = value.toString();
            String[] fields = line.split("\t");

            // Bỏ qua dòng tiêu đề (vì nó có chữ "movie_id" hoặc cột không phải số)
            if (fields.length >= 16 && !line.contains("movie_id")) {
                try {
                    double rating = Double.parseDouble(fields[14].trim()); // Cột 15
                    double votes = Double.parseDouble(fields[15].trim());  // Cột 16
                    String title = fields[2].trim(); // Cột 3

                    if (votes >= MIN_VOTES) {
                        topMovies.put(rating, title + " (Rating: " + rating + ", Votes: " + votes + ")");
                        if (topMovies.size() > N) {
                            topMovies.remove(topMovies.firstKey());
                        }
                    }
                } catch (NumberFormatException e) { }
            }
        }

        protected void cleanup(Context context) throws IOException, InterruptedException {
            for (Map.Entry<Double, String> entry : topMovies.entrySet()) {
                context.write(NullWritable.get(), new Text(entry.getValue()));
            }
        }
    }

    public static class TopNReducer extends Reducer<NullWritable, Text, NullWritable, Text> {
        private TreeMap<Double, String> topMovies = new TreeMap<>();
        private final int N = 10;

        public void reduce(NullWritable key, Iterable<Text> values, Context context) {
            for (Text value : values) {
                String line = value.toString();
                try {
                    int start = line.indexOf("(Rating: ") + 9;
                    int end = line.indexOf(",", start);
                    double rating = Double.parseDouble(line.substring(start, end));
                    topMovies.put(rating, line);
                    if (topMovies.size() > N) {
                        topMovies.remove(topMovies.firstKey());
                    }
                } catch (Exception e) { }
            }
        }

        protected void cleanup(Context context) throws IOException, InterruptedException {
            for (Map.Entry<Double, String> entry : topMovies.descendingMap().entrySet()) {
                context.write(NullWritable.get(), new Text(entry.getValue()));
            }
        }
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "Top N Movies");
        job.setJarByClass(TopNMovies.class);
        job.setMapperClass(TopNMapper.class);
        job.setReducerClass(TopNReducer.class);
        job.setOutputKeyClass(NullWritable.class);
        job.setOutputValueClass(Text.class);
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
