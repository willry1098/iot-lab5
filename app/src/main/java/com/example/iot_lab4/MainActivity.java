package com.example.iot_lab4;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.os.StrictMode;
import android.speech.RecognizerIntent;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;

public class MainActivity extends AppCompatActivity {

    Button commandButton;
    EditText speechText;
    Button weatherButton;
    Button timeButton;
    Button tweetButton;

    private static final int RECOGNIZER_RESULT = 1;

    protected boolean sendPost(String urla, String name, String value) {
        try {
            URL url = new URL(urla + "?" + name + "=" + value);

            HttpURLConnection urlc = (HttpURLConnection) url.openConnection();
            urlc.setRequestProperty("Connection", "close");
            urlc.setConnectTimeout(1000 * 5); // mTimeout is in seconds
            urlc.connect();

            if (urlc.getResponseCode() == 200) {
                System.out.println(urlc.getResponseCode());
                return new Boolean(true);
            }
        } catch (MalformedURLException e1) {
            e1.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return false;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);

        commandButton = findViewById(R.id.commandButton);
        speechText = findViewById(R.id.speechText);
        weatherButton = findViewById(R.id.weatherButton);
        timeButton = findViewById(R.id.timeButton);
        tweetButton = findViewById(R.id.tweetButton);

        commandButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent speechIntent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                speechIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                speechIntent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Speech to Text");
                startActivityForResult(speechIntent, RECOGNIZER_RESULT);
            }
        });

        weatherButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                sendPost("http://e3d3bccf41cb.ngrok.io/", "command", "weather");
            }
        });

        timeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                sendPost("http://e3d3bccf41cb.ngrok.io/", "command", "time");
            }
        });

        tweetButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent speechIntent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                speechIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                speechIntent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Speech to Text");
                startActivityForResult(speechIntent, RECOGNIZER_RESULT);
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        ArrayList<String> matches = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
        speechText.setText(matches.get(0).toString());

        super.onActivityResult(requestCode, resultCode, data);
        sendPost("http://e3d3bccf41cb.ngrok.io/", "command", matches.get(0));
    }
}