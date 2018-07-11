/**
 * Created by Alessandro on 5/31/2018.
 */

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;


public class Config_Reader {

    private String file_name;
    private String file_path;


    public Config_Reader() {


        Properties prop = new Properties();
        InputStream input = null;

        try {

            // Path of Config file
            input = new FileInputStream("/home/alessandro/IdeaProjects/Swing_Start/resources/config.properties");

            // load a properties file
            prop.load(input);

            // get the property value and print it out
            file_name = prop.getProperty("file_name");
            file_path = prop.getProperty("file_path");


        } catch (IOException ex){
            ex.printStackTrace();
        }

    }

    public String get_name(){ return file_name; }

    public String get_path(){ return file_path; }

}
