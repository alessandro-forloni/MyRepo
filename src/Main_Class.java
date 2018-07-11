import javax.swing.*;
import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.Dimension;

public class Main_Class extends JFrame{

    // Initialize here because must be read everywhere within the class
    // for button action management
    private JTextField Text_Field;

    // Build interface in constructor
    public Main_Class() {
        initComponents();
    }

    private void initComponents() {

        setTitle("Simple example");
        setSize(300, 200);

        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);

        //Add the ubiquitous "Hello World" label.
        JLabel label = new JLabel("Hello World");
        JButton button = new JButton("Run Python Code");
        Text_Field = new JTextField();

        //getContentPane().add(label);
        getContentPane().add(Text_Field);
        Text_Field.setPreferredSize( new Dimension( 200, 24 ) );

        getContentPane().add(button);

        setLayout(new FlowLayout());

        //Add button LIstener
        button.addActionListener(new ActionListener() {
               public void actionPerformed(ActionEvent evt) {
                   buttonActionPerformed(evt);
             }
         });

        //Display the window.
        //pack();
        setVisible(true);
    }

    private void buttonActionPerformed(ActionEvent evt){

        /**
         * Triggered by button
         * Reads textfield text
         * converts it to integer if possible
         * runs python code
         */

        // Handle exception for non-numeric input in text field
        try {
            int param = (int) (Double.parseDouble(Text_Field.getText()));

            Python_Runner py_run = new Python_Runner(param);
            py_run.call_code();

        } catch (java.lang.NumberFormatException ex) {
            System.err.println("Format Error in Text Field");
            return;
        }

    }


    public static void main(String[] args) {

        //creating and showing this application's GUI.

        Main_Class test = new Main_Class();
        //test.setExtendedState(JFrame.MAXIMIZED_BOTH);
    }
}
