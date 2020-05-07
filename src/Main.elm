module Main exposing (main)

import Browser
import Html exposing (Html, button, div, text)
import Html.Events exposing (onClick)
import Html.Attributes
import Random.List
import Random exposing (Generator)
import Json.Decode exposing (field, string, float)
import Json.Encode as Encode
import Random.Extra exposing (combine)
import File.Download
import Levenshtein
import Task
import Browser.Dom
import Array
import Debug


main =
  Browser.element
    { init = init
    , update = update
    , view = view
    , subscriptions = always Sub.none
    }

blockCount = 4
blockSize = 6



type Message
  = None

type alias Command = Cmd Message

type alias Model = Maybe
  { medianAge: Float
  }


type alias Data = 
  { age: Float
  , hand: String
  , gender: String
  , events: List Event 
  }

type Event 
  = Randomize (List Phrase)
  | Type Time String
  | Suggestion Time String
  | Next Time

type alias Time = Float

type alias Phrase =
  { target: String
  , suggestions: List String
  , threshold: Float
  }

init: Json.Decode.Value -> (Model, Command)
init data = 
  let 
    person = Json.Decode.field "age" Json.Decode.float
      |> Json.Decode.andThen (Json.Decode.field "hand")
    decoder = Json.Decode.array person

    model = case Json.Decode.decodeValue decoder data of 
      Ok decoded -> Just <| analyze decoded
      Err _ -> Nothing
  
  in (model, Cmd.none)

analyze ages = 
  let 
    medianAge = ages |> Array.toList |> List.sort |> List.drop (Array.length ages // 2) |> List.head |> Maybe.withDefault 0

  in 
    { medianAge = medianAge  }
  
view : Model -> Html Message
view model = case model of
  Just data -> Html.text ("median age: " ++ String.fromFloat data.medianAge)
  Nothing -> Html.text "Error"
update : Message -> Model -> (Model, Command)
update event model = (model, Cmd.none)
