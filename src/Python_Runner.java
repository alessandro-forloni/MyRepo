import java.io.File;
import java.io.IOException;
import java.lang.Process;
import java.lang.Runtime;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Python_Runner {

    int run_parameter;

    public Python_Runner(int param)  {

        this.run_parameter = param;

    }

    public void call_code() {

        //Get file name and path from config
        Config_Reader reader = new Config_Reader();

        String file_name = reader.get_name();
        String file_path = reader.get_path();

        // Create path in proper way
        File file = new File(file_path,file_name);
        //Parse parameter
        String param_string = String.valueOf(this.run_parameter);


        String python_caller = "python" + " " + file + " " + param_string;

        // Throw exception otherwise compiler complains
        try {
            Process process = Runtime.getRuntime().exec(python_caller);
            follow_execution(process);

        } catch (IOException e) {
            System.out.println(e.getMessage());
            System.out.println("An exception occurred when launching python");
        }
    }


    private void follow_execution(Process p){

        /**
         * Has the only job of checking an instance of cmd
         * and read any printed line
         * Eventually returning
         */

        String s;
        BufferedReader stdInput = new BufferedReader(new InputStreamReader(p.getInputStream()));

        try {
            while ((s = stdInput.readLine()) != null) {
                System.out.println(s);
            }
        } catch (IOException e) {
            System.out.println(e.getMessage());
            System.out.println("An exception occurred when reading cmd");
        }

    }
}



